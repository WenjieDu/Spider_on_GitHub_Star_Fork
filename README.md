# A Spider Crawling Info of Stargazers and Forkers
![](https://img.shields.io/badge/Conda-Supported-green?style=social&logo=anaconda)
![](https://img.shields.io/badge/Python-3.6-green)
![](https://img.shields.io/badge/License-MIT-lightgreen)
![](https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com%2FWenjieDu%2FGitHub_Spider_on_Star_Fork&count_bg=%233AA208&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=hits&edge_flat=false)

This spider crawls user information of stargazers and forkers of given repositories and saves such information into a `.csv` file with pandas.

Given GitHub repositories in `SPECIFIED_REPOS`, this spider will crawl all stargazers and forkers of them. If given repositories in `FILTERING_REPOS`, the spider will filter out stargazers and forkers of them from those of `SPECIFIED_REPOS`. For sure, any user in `EXCLUSION_USERS` will also be filtered out. If you want to get the email information of the crawled users, you have to provide valid GitHub credentials in file `github_credential.json`, which will be used by the spider to sign in GitHub. `spider.log` is an example log file that can show you how it works.

You can quickly create a usable python environment with an anaconda command `conda env create -f conda_env_dependencies.yml`. **❗️Note that this file is for MacOS.** Some errors may jump out if you use it on other platforms like Linux. But you can still use it for dependency reference.

<details>
<summary><b><i>👏 Click here to view stargazers and forkers of this repo </i></b></summary>

[![Stargazers repo roster for @WenjieDu/GitHub_Spider_on_Star_Fork](https://reporoster.com/stars/WenjieDu/GitHub_Spider_on_Star_Fork)](https://github.com/WenjieDu/GitHub_Spider_on_Star_Fork/stargazers)

[![Forkers repo roster for @WenjieDu/GitHub_Spider_on_Star_Fork](https://reporoster.com/forks/WenjieDu/GitHub_Spider_on_Star_Fork)](https://github.com/WenjieDu/GitHub_Spider_on_Star_Fork/network/members)
</details>
