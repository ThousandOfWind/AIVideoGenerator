<!-- Improved compatibility of back to top link: See: https://github.com/othneildrew/Best-README-Template/pull/73 -->
<a name="readme-top"></a>
<!--
*** Thanks for checking out the Best-README-Template. If you have a suggestion
*** that would make this better, please fork the repo and create a pull request
*** or simply open an issue with the tag "enhancement".
*** Don't forget to give the project a star!
*** Thanks again! Now go create something AMAZING! :D
-->



<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->

<!-- TODO -->
[//]: # ([![Contributors][contributors-shield]][contributors-url])

[//]: # ([![Forks][forks-shield]][forks-url])

[//]: # ([![Stargazers][stars-shield]][stars-url])

[//]: # ([![Issues][issues-shield]][issues-url])

[![MIT License][license-shield]][license-url]

[![LinkedIn][linkedin-shield]][linkedin-url]



<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/ThousandOfWind/AIVideoGenerator">
    <img src="docs/anchor.jpeg" alt="Logo" width="80" height="80">
  </a>

<h3 align="center">AI Video Generator</h3>

  <p align="center">
     Search news trending, collect information, and generate the news video automatically.
    <br />
    <!-- <a href="https://github.com/ThousandOfWind/AIVideoGenerator/tree/main/docs"><strong>Explore the docs »</strong></a>
    <br />
    <br /> -->
    <a href="https://player.youku.com/embed/XNjMwNjE1NDEyNA==">View Generated Video</a>
    ·
    <a href="https://github.com/ThousandOfWind/AIVideoGenerator/issues">Report Bug</a>
    ·
    <a href="https://github.com/ThousandOfWind/AIVideoGenerator/issues">Request Feature</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project
This project focuses on generating short videos based on news webpages. It begins by parsing the content of the news webpage, after which it utilizes the GPT4 model to generate a news anchor script. Based on this script, appropriate images are collected or generated. All these materials are then compiled to create a news short video. The final generated video cites the news source and each image includes a website watermark for reference.

This project is under developing, so interface may change anytime.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



### Built With

* [![Azure][Azure.com]][Azure-url]
* [![Openai][Openai.com]][Openai-url]

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

To get a local copy up and running follow these simple example steps.

### Prerequisites

* Have an Azure account
* Create [Azure Openai Service](https://azure.microsoft.com/en-us/products/ai-services/openai-service/)
* Create [Azure Speech Service](https://azure.microsoft.com/en-us/products/ai-services/text-to-speech/)
* Create [Bing Search Service](https://learn.microsoft.com/en-us/bing/search-apis/)

### Installation

1. Clone the repo
   ```sh
   git clone https://github.com/ThousandOfWind/AIVideoGenerator.git
   ```
2. Make sure you are above python 3.9, and install python packages
   ```sh
   pip install -r requirement.txt
   ```
3. Creat a `.env` file in root path, then enter your endpoint and key
   ```dotenv
    OPANAI_API_ENDPOINT=https://{}.openai.azure.com/
    OPANAI_API_KEY={}
    SPEECH_HOST=customvoice.api.speech.microsoft.com            
    SPEECH_KEY={}
    SPEECH_REGION={}
    BING_SEARCH_ENDPOINT=https://api.bing.microsoft.com/v7.0/
    BING_SEARCH_KEY={}
   ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage

Take `ExampleVideoGen.py` as an example that generate a video for 1st sport news in China.

### Get News Trending

To get news, use `BingSearchAdapter` in `tools/bing_search_adapter.py`. It depends on your bing search service. A free plan is enough for this project.

```python
from tools.bing_search_adapter import BingSearchAdapter, ChinaCategory, Market

bing = BingSearchAdapter(
    bing_search_api=os.getenv('BING_SEARCH_ENDPOINT'), 
    bing_search_key=os.getenv('BING_SEARCH_KEY')
)
newsList = bing.newsCategoryTrending(ChinaCategory.Sports.value, Market.China.value)
```

Now you got a list of news. If you want to got the news in other ways, just keep in mind, name, url and provider are required. Following is a dict for a news.

```python
{
  "name": Name of your news
  "provider": [
    {
      "name": Name of one of your news provider
    }
  ],
  "url": Url of your news
}
```

### Generate Video 
`AIDirector` in `workers/AIDirector` is all you need to generate Video. To generate video automatically, it depends on bing search, openai, and azure speech service.

```python
oai = OpenaiAdapter(openai_client=AzureOpenAI(
    api_version="2023-12-01-preview",
    azure_endpoint=os.getenv('OPANAI_API_ENDPOINT'),
    api_key=os.getenv('OPANAI_API_KEY'),
))
speech = SpeechServiceAdapter(os.getenv('SPEECH_HOST'), os.getenv('SPEECH_REGION'), os.getenv('SPEECH_KEY'), DefaultMaleSpeaker)

director = AIDirector(oai, speech, bing, '/System/Library/Fonts/Supplemental/Arial Unicode.ttf')

director.news2Video(news, folderPath=getCurrentTimeAsFolder())
```

For Chinese caption, font path is required. `'/System/Library/Fonts/Supplemental/Arial Unicode.ttf'` is path to my system font.


`director.news2Video` includes 3 steps, feel free to customize any of them to customize your video.
1. generate script from new.
2. prepare multi-media resource for the news, e.g. image, audio and so on.
3. Use all of the resource to be the video

```python
script = director.new2script(news, output_dir)
enriched_script = director.script2multimedia(script, news, output_dir)
director.enriched_script2video(enriched_script, output_dir)
```

### With Avatar

try it with Take `ExampleVideoGenWIthAvatar.py` as an example that generate a video for 1st sport news in China.


The project integrates 2 kind of avatar. 
* The female speaker is integrated with Azure text to avatar, it require a non-free plan in limited region, please refer to [Azure Speech Service](https://azure.microsoft.com/en-us/products/ai-services/text-to-speech/) for details. The avatar video should overlay on news image, BUT it actually cover the news. I don't know how to fix now, so just let it go. It will only shown up during the first sentence, and when no good image for the news.
* The male speaker, however have not have a avatar in Azure, so i draw image by Dall·E model when a avatar is required. The same with female speaker, it will only shown up during the first sentence, and when no good image for the news.


```python
director.news2Video(newsList[0], folderPath, with_avatar=True)
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ROADMAP -->
## Roadmap

- [ ] webpage to script
  - [x] news webpage to script
  - [ ] any webpage to script
  - [ ] any topic to script
- [x] Collect/Generate multimedia resource for a script
  - [x] Text to speech
  - [x] Search online image for text
  - [x] Draw image if no ideal existing image
  - [x] Speech to avatar
  - [ ] Search online video/gif for text
- [x] Merge all resource to video
- [ ] Video improvement
  - [ ] remove white background of avatar / change to another way to add avatar
  - [ ] Improve word segmentation, tone and gesture
  - [ ] Better turnaround
  - [ ] Add BGM
  - [ ] Fix Avatar background issue, Avatar position and size auto-adjust
- [ ] [Current on going] Go deeper into content
  - [ ] download image/video in webpage
  - [ ] Add OCR when review image for news
  - [ ] Search related information
  - [ ] Draw table / chart if need
- [ ] UX
  - [ ] UI Design
  - [ ] GUI
  - [ ] CMD
  - [ ] REST
- [ ] Integrate social media
- [ ] Integrate Lang Chain
- [ ] Onboard GPT store
- [ ] Monitor time and cost for a generation
    
<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTACT -->
## Contact

Julie Zhu - julie1996@foxmail.com

Project Link: [https://github.com/ThousandOfWind/AIVideoGenerator](https://github.com/ThousandOfWind/AIVideoGenerator)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

* BGM from: https://www.fiftysounds.com/zh/

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/ThousandOfWind/AIVideoGenerator.svg?style=for-the-badge
[contributors-url]: https://github.com/ThousandOfWind/AIVideoGenerator/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/ThousandOfWind/AIVideoGenerator.svg?style=for-the-badge
[forks-url]: https://github.com/ThousandOfWind/AIVideoGenerator/network/members
[stars-shield]: https://img.shields.io/github/stars/ThousandOfWind/AIVideoGenerator.svg?style=for-the-badge
[stars-url]: https://github.com/ThousandOfWind/AIVideoGenerator/stargazers
[issues-shield]: https://img.shields.io/github/issues/ThousandOfWind/AIVideoGenerator.svg?style=for-the-badge
[issues-url]: https://github.com/ThousandOfWind/AIVideoGenerator/issues
[license-shield]: https://img.shields.io/github/license/ThousandOfWind/AIVideoGenerator.svg?style=for-the-badge
[license-url]: https://github.com/ThousandOfWind/AIVideoGenerator/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/julie-zhu-8b8b35143
[product-screenshot]: images/screenshot.png
[Azure.com]: https://img.shields.io/badge/microsoftazure-069af3?style=for-the-badge&logo=microsoftazure
[Azure-url]: https://azure.microsoft.com/
[Openai.com]: https://img.shields.io/badge/openai-000000?style=for-the-badge&logo=openai
[Openai-url]: https://openai.com/ 

