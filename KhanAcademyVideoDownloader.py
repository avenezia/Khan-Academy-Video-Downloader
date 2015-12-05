import argparse
import os
import requests
import sys

class KhanAcademyVideoDownloader:

    def __init__(self):
        self._kindString = "kind"
        self._topicString = "Topic"
        self._videoString = "Video"

        self._topicUrl = "http://www.khanacademy.org/api/v1/topic/"
        self._videoUrl = "http://www.khanacademy.org/api/v1/videos/"

        self._fileExtension = "mp4"
        self._filePath = []

    def parseCommandLineArguments(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("course_name", type=str, help="The name of the course you want to download the videos of.")
        parser.add_argument("-e", type=str, help="The extension of the videos to be downloaded", metavar="video_extension")
        args = parser.parse_args()
        if args.e is not None:
            if len(args.e) > 1:
                self._fileExtension = args.e
            else:
                print "The provided extension is too short, by default using mp4."
        return args.course_name

    def visitCourse(self, topic):
        self._filePath.append(topic)
        self.visitElement(requests.get(self._topicUrl + topic).json())

    def visitElement(self, element):
        elementKind = element[self._kindString]
        if elementKind == self._topicString:
            self.visitTopic(element)
        elif elementKind == self._videoString:
            self.visitVideo(element)

    def visitTopic(self, topicElement):
        self._childrenString = "children"
        self._idString = "id"

        childCounter = 0
        for child in topicElement[self._childrenString]:
            childId = child[self._idString]
            childKind = child[self._kindString]

            if childKind == self._topicString:
                url =  self._topicUrl + childId
            elif childKind == self._videoString:
                url = self._videoUrl + childId

            childCounter += 1
            self._filePath.append(str(childCounter) + "_" + child[self._idString])
            self.visitElement(requests.get(url).json())
            self._filePath.pop()

    def visitVideo(self, videoElement):
        downloadUrls = videoElement["download_urls"]
        if self._fileExtension in downloadUrls:
            fileRequest = requests.get(downloadUrls[self._fileExtension], stream=True)
            fileName = "/".join(self._filePath) + "." + self._fileExtension
            print "Downloading " + fileName
            self.saveFile(fileRequest, fileName)

    def saveFile(self, fileRequest, fileName):
        if not os.path.exists(os.path.dirname(fileName)):
            os.makedirs(os.path.dirname(fileName))

        chunkSize = 2 ** 16
        with open(fileName, 'wb') as fileDescriptor:
            for chunk in fileRequest.iter_content(chunkSize):
                fileDescriptor.write(chunk)

def main():
    k = KhanAcademyVideoDownloader()
    k.visitCourse(k.parseCommandLineArguments())

if __name__ == '__main__':
    main()