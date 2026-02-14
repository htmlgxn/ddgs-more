from ddgs.engines.youtube_videos import YoutubeVideos


def test_youtube_extract_results() -> None:
    html = """
    <html><head></head><body>
    <script>
    var ytInitialData = {
      "contents": {
        "twoColumnSearchResultsRenderer": {
          "primaryContents": {
            "sectionListRenderer": {
              "contents": [{
                "itemSectionRenderer": {
                  "contents": [{
                    "videoRenderer": {
                      "videoId": "abc123xyz",
                      "title": {"runs": [{"text": "Sample Video"}]},
                      "descriptionSnippet": {"runs": [{"text": "Sample description"}]},
                      "lengthText": {"simpleText": "12:34"},
                      "publishedTimeText": {"simpleText": "3 days ago"},
                      "ownerText": {"runs": [{"text": "Uploader"}]},
                      "viewCountText": {"simpleText": "42K views"},
                      "thumbnail": {"thumbnails": [{"url": "https://img.example/1.jpg"}]}
                    }
                  }]
                }
              }]
            }
          }
        }
      }
    };
    </script>
    </body></html>
    """

    engine = YoutubeVideos()
    results = engine.extract_results(html)

    assert len(results) == 1
    assert results[0].title == "Sample Video"
    assert results[0].content == "https://www.youtube.com/watch?v=abc123xyz"
    assert results[0].embed_url == "https://www.youtube.com/embed/abc123xyz"
    assert results[0].uploader == "Uploader"
