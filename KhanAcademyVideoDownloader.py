import requests
import sys

class KhanAcademyVideoDownloader:

    def __init__(self):
        self._kindString = "kind"
        self._topicString = "Topic"
        self._videoString = "Video"

        self._topicUrl = "http://www.khanacademy.org/api/v1/topic/"
        self._videoUrl = "http://www.khanacademy.org/api/v1/videos/"

    def visitCourse(self, topic):
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
        print "Visiting " + topicElement[self._idString]
        for child in topicElement[self._childrenString]:
            childId = child[self._idString]
            childKind = child[self._kindString]
            if childKind == self._topicString:
                print "Ready to visit topic " + childId
                url =  self._topicUrl + childId
            elif childKind == self._videoString:
                print "Ready to visit video " + childId
                url = self._videoUrl + childId
            self.visitElement(requests.get(url).json())

    def visitVideo(self, videoElement):
        #TODO: write files following the hierarchy of topics.
        title = videoElement["title"]
        downloadUrls = videoElement["download_urls"]
        if "mp4" in downloadUrls:
            fileRequest = requests.get(downloadUrls["mp4"], stream=True)
            fileName = title.replace(" ", "_") + ".mp4"
            print "Downloading " + fileName
            with open(fileName, 'wb') as fd:
                for chunk in fileRequest.iter_content(16384):
                    fd.write(chunk)

def main():
    #TODO: proper argument parsing.
    k = KhanAcademyVideoDownloader()
    k.visitCourse(sys.argv[1])

if __name__ == '__main__':
    main()