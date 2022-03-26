"""
This spider is created by WenjieDu to crawl information of stargazers and forkers of specified repositories on GitHub.
"""
import argparse
import json
import logging
import os
import random
from time import sleep

import pandas as pd
import requests
from bs4 import BeautifulSoup

##################################################################################################
# Here are configurations you have to set
##################################################################################################

# repos that you want to crawl star and fork user info from
SPECIFIED_REPOS = [

]
# repos that you want to use for filtering
FILTERING_REPOS = [

]
# users that you want to manually exclude
EXCLUSION_USERS = [

]

USE_PROXY = False  # whether to use proxy
PROXY_POOL_URL = 'http://127.0.0.1:8000'  # pool url where you fetch proxies

# Manual configurations end here
##################################################################################################

SITE_DOMAIN = 'https://github.com'
STAR = "stargazers"
FORK = "network/members"

# STAR PLACEHOLDER start from 1
STAR_SELECTOR = "#repos > ol"
# FORK PLACEHOLDER start from 2
FORK_SELECTOR = "#network"
# user info selector
FULL_NAME_SELECTOR = "#js-pjax-container > div.container-xl.px-3.px-md-4.px-lg-5 > div > div.Layout-sidebar > div > div.js-profile-editable-replace > div.clearfix.d-flex.d-md-block.flex-items-center.mb-4.mb-md-0 > div.vcard-names-container.float-left.js-profile-editable-names.col-12.py-3.js-sticky.js-user-profile-sticky-fields > h1 > span.p-name.vcard-fullname.d-block.overflow-hidden"
LOCATION_SELECTOR = "#js-pjax-container > div.container-xl.px-3.px-md-4.px-lg-5 > div > div.Layout-sidebar > div > div.js-profile-editable-replace > div.d-flex.flex-column > div.js-profile-editable-area.d-flex.flex-column.d-md-block > ul > li.vcard-detail.pt-1.css-truncate.css-truncate-target.hide-sm.hide-md > span.p-label"
COMPANY_SELECTOR = "#js-pjax-container > div.container-xl.px-3.px-md-4.px-lg-5 > div > div.Layout-sidebar > div > div.js-profile-editable-replace > div.d-flex.flex-column > div.js-profile-editable-area.d-flex.flex-column.d-md-block > ul > li.vcard-detail.pt-1.css-truncate.css-truncate-target.hide-sm.hide-md > span.p-org > div"
EMAIL_SELECTOR = "#js-pjax-container > div.container-xl.px-3.px-md-4.px-lg-5 > div > div.Layout-sidebar > div > div.js-profile-editable-replace > div.d-flex.flex-column > div.js-profile-editable-area.d-flex.flex-column.d-md-block > ul > li> a.u-email"
WEBSITE_SELECTOR = "#js-pjax-container > div.container-xl.px-3.px-md-4.px-lg-5 > div > div.Layout-sidebar > div > div.js-profile-editable-replace > div.d-flex.flex-column > div.js-profile-editable-area.d-flex.flex-column.d-md-block > ul > li[itemprop=url] > a"
TWITTER_SELECTOR = "#js-pjax-container > div.container-xl.px-3.px-md-4.px-lg-5 > div > div.Layout-sidebar > div > div.js-profile-editable-replace > div.d-flex.flex-column > div.js-profile-editable-area.d-flex.flex-column.d-md-block > ul > li.hide-md > a"

USER_AGENTS = [
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
    "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
    "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
    "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
    "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
    "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
    "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
    "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.11 TaoBrowser/2.0 Safari/536.11",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71 Safari/537.1 LBBROWSER",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; LBBROWSER)",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E; LBBROWSER)",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.84 Safari/535.11 LBBROWSER",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E)",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; QQBrowser/7.0.3698.400)",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SV1; QQDownload 732; .NET4.0C; .NET4.0E; 360SE)",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E)",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.89 Safari/537.1",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.89 Safari/537.1",
    "Mozilla/5.0 (iPad; U; CPU OS 4_2_1 like Mac OS X; zh-cn) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8C148 Safari/6533.18.5",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:2.0b13pre) Gecko/20110307 Firefox/4.0b13pre",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:16.0) Gecko/20100101 Firefox/16.0",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11",
    "Mozilla/5.0 (X11; U; Linux x86_64; zh-CN; rv:1.9.2.10) Gecko/20100922 Ubuntu/10.10 (maverick) Firefox/3.6.10"
]


def get_header():
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Accept-Encoding': 'gzip, deflate',
    }


def setup_logger(log_file_path, mode='a'):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler(log_file_path, mode=mode)
    fh.setLevel(logging.INFO)

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger


def get_proxy():
    if random.randint(0, 10) > 4:  # 50% to use proxy, you can adjust it if you like
        all_proxies = json.loads(requests.get(PROXY_POOL_URL).text)
        all_proxies = [i for i in all_proxies if i[2] > 4]
        # logger.info(f'Total proxy num: {len(all_proxies)}')
        picked = random.choice(all_proxies)
        return {'http': f'http://{picked[0]}:{picked[1]}'}
    else:
        sleep(2)  # if use local ip, then set delay
        return None


def request_url(url, sess=None):
    while True:
        try:
            header = get_header()
            picked_proxy = get_proxy() if USE_PROXY else None
            if sess:
                response = sess.get(url, headers=header, timeout=(25, 30), proxies=picked_proxy)
            else:
                response = requests.get(url, headers=header, timeout=(25, 30), proxies=picked_proxy)
        except:
            # logger.info('Proxy failed once, try again')
            continue
        if response.status_code == 200:
            break
        else:
            sleep(3)
        logger.info('Request failed once, try again')
    return BeautifulSoup(response.text, 'lxml')


def crawl_user_from_repos(repos):
    """ crawl star and fork users from specified repos
    :param repos: specified github repo names
    :return: crawled users in one list
    """
    users = set()
    for repo in repos:
        repo_url = os.path.join(SITE_DOMAIN, repo)
        logger.info(f'Start to crawl info from repo {repo_url}')
        repo_star_page = os.path.join(repo_url, STAR)
        repo_fork_page = os.path.join(repo_url, FORK)
        star_set, fork_set = [], []

        # request docs of star page and gather stargazers, num of stargazer page may be more than one
        logger.info(f'Crawling {repo_star_page}...')
        soup = request_url(repo_star_page)
        while True:
            stargazer_block = soup.select_one(STAR_SELECTOR)  # select the whole block
            stargazer_block = set([i for i in stargazer_block])
            stargazer_block.remove('\n')
            for i in stargazer_block:
                star_set.append(
                    i.select_one("div > div.ml-3.flex-auto.min-width-0 > h3 > span > span > a").text
                )
            next_page = soup.select("#repos > div.paginate-container > div > a")
            if next_page and next_page[-1].text == 'Next':
                soup = request_url(next_page[-1]['href'])
            else:
                break

        # request docs of fork page and gather forkers, forkers are all on one page
        logger.info(f'Crawling {repo_fork_page}...')
        soup = request_url(repo_fork_page)
        forker_block = soup.select_one(FORK_SELECTOR)  # select the whole block
        forker_block = set([i for i in forker_block][2:])  # the first two need to be removed
        forker_block.remove('\n')
        for i in forker_block:
            fork_set.append(i.select_one("div> a:nth-child(3)").text)
        # get union of stargazers and forkers
        union_set = set(star_set).union(set(fork_set))
        users = users.union(union_set)
    return set(users)


def crawl_user_info(users, sess):
    """ craw user info from their profile page
    :param users:
    :param sess: session with github account login. Email info is not available if the session is invalid.
    :return: crawled user info in pandas dataframe
    """
    df = pd.DataFrame(
        columns=['user', 'full_name', 'location', 'company', 'email', 'website', 'twitter']
    )
    for user in users:
        logger.info(f'Crawling info of user {user}...')
        user_page = os.path.join(SITE_DOMAIN, user)
        # request docs of user page and gather user info
        soup = request_url(user_page, sess)
        try:
            full_name = soup.select_one(FULL_NAME_SELECTOR).text
        except:
            full_name = None
        try:
            location = soup.select_one(LOCATION_SELECTOR).text
        except:
            location = None
        try:
            company = soup.select_one(COMPANY_SELECTOR).text
        except:
            company = None
        try:
            email = soup.select_one(EMAIL_SELECTOR).text
        except:
            email = None
        try:
            website = soup.select_one(WEBSITE_SELECTOR).text
        except:
            website = None
        try:
            twitter = soup.select_one(TWITTER_SELECTOR).text
        except:
            twitter = None
        info_dict = {'user': user,
                     'full_name': full_name,
                     'location': location,
                     'company': company,
                     'email': email,
                     'website': website,
                     'twitter': twitter}
        df = df.append(info_dict, ignore_index=True)
    return df


def bool(op):
    if op.lower() == ('true' or 'yes' or 'y' or 't'):
        return True
    else:
        return False


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--crawl_different_users', type=bool, default=True,
                        help='whether to crawl detailed info of different users')
    parser.add_argument('--crawl_same_users', type=bool, default=False,
                        help='whether to crawl detailed info of same users')
    parser.add_argument('--ensure_successful_github_login', type=bool, default=True,
                        help='whether to ensure login github successful, namely you want to crawl emails')
    args = parser.parse_args()
    logger = setup_logger("spider.log", mode='w')
    logger.info(args)

    # crawl users that already star or fork EXCLUSION_REPOS
    interested_users = crawl_user_from_repos(SPECIFIED_REPOS)
    excluded_users = crawl_user_from_repos(FILTERING_REPOS)
    if len(EXCLUSION_USERS) > 0:
        excluded_users = excluded_users.union(set(EXCLUSION_USERS))
    different_users = list(
        set(interested_users).difference(set(excluded_users))
    )
    same_users = list(
        set(interested_users).intersection(set(excluded_users))
    )
    logger.info(f"Got {len(different_users)} different users: \n {different_users}")
    logger.info(f"Got {len(same_users)} same users: \n {same_users}")

    if args.crawl_same_users or args.crawl_different_users:
        with open('github_credential.json') as f:
            credential = json.load(f)
        github_username = credential["username"]
        github_password = credential["password"]
        login_url = 'https://github.com/login'
        session_url = 'https://github.com/session'

        with requests.session() as session:
            # login github
            logger.info('Signing in GitHub...')
            login_html = session.get(login_url).content.decode()
            bs = BeautifulSoup(login_html, features="html.parser")
            input_label = bs.find(attrs={"name": "authenticity_token"})
            authenticity_token = input_label.attrs["value"]
            # build request arguments for login api
            data = {
                "commit": "Sign in",
                "authenticity_token": authenticity_token,
                "login": github_username,
                "password": github_password,
                "webauthn-support": "supported"
            }
            session.post(session_url, data=data)
            response = session.get("https://github.com/settings/profile")
            settings_html = session.get("https://github.com/settings/profile").content.decode()
            bs = BeautifulSoup(settings_html, features="html.parser")
            if bs.title.string == "Your Profile":
                logger.info('Login successfully.')
            else:
                logger.warning('Login failed. Please check your github username and password.')
                if args.ensure_successful_github_login:
                    logger.error('Quit now because of failed login.')
                    quit()

            # crawling user info
            if args.crawl_same_users:
                logger.info('Crawling info_same_users...')
                info_same_users = crawl_user_info(same_users, session)
                logger.info('Saving info_same_users into csv file...')
                info_same_users.to_csv('crawled_same_users.csv')
            if args.crawl_different_users:
                logger.info('Crawling info_different_users...')
                info_different_users = crawl_user_info(different_users, session)
                logger.info('Saving info_different_users into csv file...')
                info_different_users.to_csv('crawled_different_users.csv')

    logger.info('All finished.')
