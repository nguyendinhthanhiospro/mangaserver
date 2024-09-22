from datetime import datetime
import json
import math
import re
import time
from flask import jsonify, request, session
from bs4 import BeautifulSoup
import requests
import urllib
import urllib.parse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, WebDriverException
from fake_useragent import UserAgent

from main import (
    check_chapter,
    check_image_chapter,
    check_manga,
    insertImageChapter,
    insertListChapter,
    insertMangaIntoTable,
    make_link,
    split_join,
)


def create_driver(timeout):
    # Fake user agent
    ua = UserAgent()
    fake_ua = ua.random
    fake_ua = (
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0"
    )

    # By pass web
    options = webdriver.ChromeOptions()
    prefs = {
        "profile.managed_default_content_settings.images": 2,  # Disable images
        "profile.managed_default_content_settings.stylesheets": 2,  # Disable CSS
        "profile.managed_default_content_settings.cookies": 2,  # Disable cookies
        "profile.managed_default_content_settings.javascript": 1,  # Enable JavaScript if needed
        "profile.managed_default_content_settings.plugins": 2,  # Disable plugins
        "profile.managed_default_content_settings.popups": 2,  # Disable popups
        "profile.managed_default_content_settings.geolocation": 2,  # Disable geolocation
        "profile.managed_default_content_settings.media_stream": 2,  # Disable media stream
    }
    options.add_experimental_option("prefs", prefs)
    options.add_argument("--headless")
    options.add_argument(f"user-agent={fake_ua}")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-images")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=options
    )
    driver.set_page_load_timeout(timeout)
    driver.set_script_timeout(10)
    driver.implicitly_wait(10)

    return driver


def is_error_page(page_source):
    return "Cloudflare" in page_source


def by_pass_data(url, timeout, retries=1000, delay=3):
    try:
        attempt = 0
        while attempt < retries:
            driver = create_driver(timeout)
            attempt += 1
            # print(attempt)
            try:
                driver.get(url)
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                content = driver.page_source
                if is_error_page(content):
                    # print(content)
                    print("Cloudflare")
                    continue
                return content
            except Exception as e:
                # print(f"An error occurred: {e}")
                time.sleep(delay)

        driver.quit()
        return None
    except Exception as e:
        # print(e)
        return jsonify({"message": f"Error: {e}"})


# MANGANELO
def get_lasted_manga_updates_server_1():
    base_link = "https://ww5.manganelo.tv"
    session["server"] = 1
    full_latest_update = []
    link = "https://ww5.manganelo.tv/home"
    localhost = split_join(request.url)
    request_home = requests.get(link)
    soup_home = BeautifulSoup(request_home.text, "html.parser")

    for lastest_update in soup_home.find_all("div", class_="content-homepage-item"):
        manga_link_original = ""
        try:
            manga_link_original = base_link + lastest_update.find(
                "a", {"data-tooltip": "sticky_33975"}
            ).get("href")
        except:
            pass

        path_segment_manga = manga_link_original.split("/")[-1]

        manga_title = ""
        try:
            manga_title = lastest_update.find(
                "a", {"data-tooltip": "sticky_33975"}
            ).get("title")
        except:
            pass

        manga_poster = ""
        try:
            manga_poster = base_link + lastest_update.find(
                "a", {"data-tooltip": "sticky_33975"}
            ).find("img", {"class": "img-loading"}).get("data-src")
        except:
            pass

        description_manga = ""

        chapters = []
        try:
            chapters = lastest_update.find_all("p", {"class": "a-h item-chapter"})
        except:
            pass

        chapter_link_original = ""
        try:
            chapter_link_original = base_link + chapters[0].find("a").get("href")
        except:
            pass

        chapter_title = ""
        try:
            chapter_title = chapters[0].find("a").text
        except:
            pass

        path_segment_chapter = chapter_link_original.split("/")[-1]

        manga_link_server = make_link(localhost, f"/web/rmanga/1/{path_segment_manga}/")
        chapter_link_server = make_link(
            localhost, f"/web/rmanga/1/{path_segment_manga}/{path_segment_chapter}/"
        )

        manga_detail = {
            "id_manga": manga_link_original,
            "title_manga": manga_title,
            "image_poster_link_goc": manga_poster,
            "description_manga": description_manga,
            "path_segment_manga": path_segment_manga,
            "url_manga": manga_link_server,
            "chapter_new": chapter_title,
            "path_segment_chapter": path_segment_chapter,
            "url_chapter": chapter_link_server,
        }
        full_latest_update.append(manga_detail)

    return full_latest_update


def get_hot_manga_server_1():
    base_link = "https://ww5.manganelo.tv"
    session["server"] = 1
    hot_manga = []
    link = "https://ww5.manganelo.tv/genre?type=topview"
    localhost = split_join(request.url)
    request_home = requests.get(link)
    soup_home = BeautifulSoup(request_home.text, "html.parser")

    list_hot_manga = soup_home.find("div", class_="panel-content-genres")
    for manga in list_hot_manga.find_all("div", class_="content-genres-item"):
        id_manga = ""
        try:
            id_manga = base_link + manga.find("a", class_="genres-item-img").get("href")
        except:
            pass

        path_segment_manga = id_manga.split("/")[-1]

        manga_title = ""
        try:
            manga_title = base_link + manga.find("a", class_="genres-item-img").get(
                "title"
            )
        except:
            pass

        manga_poster = ""
        try:
            manga_poster = base_link + manga.find("a", class_="genres-item-img").find(
                "img"
            ).get("src")
        except:
            pass

        description_manga = ""

        id_chapter = ""
        try:
            id_chapter = base_link + manga.find(
                "a", class_="genres-item-chap text-nowrap a-h"
            ).get("href")
        except:
            pass

        chapter_title = ""
        try:
            chapter_title = manga.find(
                "a", class_="genres-item-chap text-nowrap a-h"
            ).text
        except:
            pass

        path_segment_chapter = id_chapter.split("/")[-1]
        manga_link_server = make_link(localhost, f"/web/rmanga/1/{path_segment_manga}/")
        chapter_link_server = make_link(
            localhost, f"/web/rmanga/1/{path_segment_manga}/{path_segment_chapter}/"
        )

        manga_detail = {
            "id_manga": id_manga,
            "title_manga": manga_title,
            "image_poster_link_goc": manga_poster,
            "description_manga": description_manga,
            "path_segment_manga": path_segment_manga,
            "url_manga": manga_link_server,
            "chapter_new": chapter_title,
            "path_segment_chapter": path_segment_chapter,
            "url_chapter": chapter_link_server,
        }
        hot_manga.append(manga_detail)

    return hot_manga


def get_manga_server_1(path):
    base_link = "https://ww5.manganelo.tv"
    link = f"https://ww5.manganelo.tv/manga/{path}"
    request_manga = requests.get(link)
    localhost = split_join(request.url)
    soup_manga = BeautifulSoup(request_manga.text, "html.parser")
    manga = soup_manga.find("div", {"class": "container-main-left"})

    # Get title manga + path_segment_manga
    tmp = manga.find("div", {"class": "panel-breadcrumb"}).find_all(
        "a", {"class": "a-h"}
    )
    path_segment_manga = path
    manga_title = tmp[1].text
    manga_title = manga_title.replace("\n", "")
    manga_title = re.sub("  +", "", manga_title)

    manga_poster = base_link + manga.find("div", {"class": "panel-story-info"}).find(
        "img", {"class": "img-loading"}
    ).get("src")

    # Get author + catergories
    tmp = manga.find("div", {"class": "panel-story-info"}).find_all(
        "td", {"class": "table-value"}
    )
    authors = tmp[1].find_all("a", {"class": "a-h"})
    for i in range(len(authors)):
        authors[i] = authors[i].text
    str_authors = ", ".join(authors)

    status = tmp[2].text
    status = status.replace("\n", "")
    status = re.sub("  +", "", status)

    categories = tmp[-1].find_all("a", {"class": "a-h"})
    for i in range(len(categories)):
        categories[i] = categories[i].text
    str_categories = ", ".join(categories)

    description = manga.find("div", {"class": "panel-story-info-description"}).text
    description = (
        description.replace("Description :", "").replace("\n", "").replace("\r", "")
    )
    description = re.sub("  +", "", description)

    list_chapter = manga.find_all("li", {"class": "a-h"})
    chapters = {}
    chapter_titles = []
    for chapter in list_chapter:
        chapter_title = chapter.find("a").text
        chapter_titles.append(chapter_title)
        chapter_link_original = base_link + chapter.find("a").get("href")
        path_segment_chapter = chapter_link_original.split("/")[-1]
        chapter_link_server = make_link(
            localhost, f"/web/rmanga/1/{path_segment_manga}/{path_segment_chapter}/"
        )
        chapters[f"{chapter_title}"] = chapter_link_server

    str_chapters = ", ".join(chapter_titles)

    manga_info = {
        "genres": "manga",
        "id_manga": link,
        "title": manga_title,
        "description": description,
        "poster": manga_poster,
        "categories": str_categories,
        "status": status,
        "author": str_authors,
        "chapters": chapters,
    }

    try:
        if check_manga(path):
            insertMangaIntoTable(
                link,
                "0",
                "5.0",
                description,
                manga_poster,
                link,
                str_chapters,
                str_authors,
                str_categories,
                status,
                manga_title,
                base_link,
                "",
            )
    except:
        pass

    return manga_info


def get_image_chapter_server_1(path, id_chapter):
    images = []
    id_manga = f"https://ww5.manganelo.tv/manga/{path}"
    link_chapter = f"https://ww5.manganelo.tv/chapter/{path}/{id_chapter}/"
    request = requests.get(link_chapter)
    soup_chapter = BeautifulSoup(request.text, "html.parser")

    # GET MANGA_TITLE, CHAPTER_TITLE
    tmp = (
        soup_chapter.find("div", {"class": "body-site"})
        .find("div", {"class": "panel-breadcrumb"})
        .find_all("a", {"class": "a-h"})
    )
    manga_title = tmp[1].text
    chapter_title = tmp[-1].text

    list_image = soup_chapter.find("div", {"class": "container-chapter-reader"})
    for image in list_image.find_all("img"):
        images.append(image.get("data-src"))

    chapter_info = {
        "title": manga_title,
        "image_chapter": images,
        "chapter_title": chapter_title,
    }

    try:
        if check_chapter(link_chapter):
            insertListChapter(link_chapter, chapter_title, id_chapter, id_manga)
    except:
        pass

    try:
        str_images = ",".join(images)
        if check_image_chapter(path, id_chapter):
            insertImageChapter(f"{path}-{id_chapter}", link_chapter, "", str_images)
    except:
        pass

    return chapter_info


# MANGAREADER
def get_lasted_manga_updates_server_2():
    base_link = "https://www.mangareader.cc"
    session["server"] = 2
    full_latest_update = []
    localhost = split_join(request.url)
    request_home = requests.get(base_link)
    soup_home = BeautifulSoup(request_home.text, "html.parser")

    lastest_update_mangas = soup_home.find("div", class_="allgreen")
    for lastest_update in lastest_update_mangas.find_all("div", class_="mng"):
        id_manga = lastest_update.find("a", class_="series").get("href")
        manga_poster = lastest_update.find("a", class_="series").find("img").get("src")
        manga_title = (
            lastest_update.find("div", class_="title")
            .find("a", class_="series")
            .get("title")
        )
        chapter_new = lastest_update.find_all("li")
        id_chapter = chapter_new[0].find("a").get("href")
        chapter_title = chapter_new[0].find("a").get("title")
        path_segment_manga = id_manga.split("/")[-1]
        path_segment_chapter = id_chapter.split("/")[-1]

        manga_link_server = make_link(localhost, f"/web/rmanga/2/{path_segment_manga}/")
        chapter_link_server = make_link(
            localhost, f"/web/rmanga/2/{path_segment_manga}/{path_segment_chapter}/"
        )

        manga_detail = {
            "id_manga": id_manga,
            "title_manga": manga_title,
            "image_poster_link_goc": manga_poster,
            "description_manga": "",
            "path_segment_manga": path_segment_manga,
            "url_manga": manga_link_server,
            "chapter_new": chapter_title,
            "path_segment_chapter": path_segment_chapter,
            "url_chapter": chapter_link_server,
        }
        full_latest_update.append(manga_detail)

    return full_latest_update


def get_popular_manga_server_2():
    base_link = "https://www.mangareader.cc"
    link = "https://www.mangareader.cc/popular-manga"
    full_popular_manga = []
    localhost = split_join(request.url)
    request_home = requests.get(link)
    soup_home = BeautifulSoup(request_home.text, "html.parser")

    popular_mangas = soup_home.find("div", class_="allgreen genrelst")
    for manga in popular_mangas.find_all("div", class_="anipost"):
        id_manga = ""
        try:
            id_manga = manga.find("div", class_="thumb").find("a").get("href")
        except:
            pass

        title_manga = ""
        try:
            title_manga = manga.find("div", class_="thumb").find("a").get("title")
        except:
            pass

        poster_manga = ""
        try:
            poster_manga = (
                manga.find("div", class_="thumb").find("a").find("img").get("src")
            )
        except:
            pass

        chapter_info = manga.find("div", class_="info").find_all("span")[2]

        id_chapter = ""
        try:
            id_chapter = chapter_info.find("a").get("href")
        except:
            pass

        title_chapter = ""
        try:
            title_chapter = chapter_info.find("a").text.strip()
        except:
            pass

        path_segment_manga = id_manga.split("/")[-1]
        path_segment_chapter = id_chapter.split("/")[-1]
        manga_link_server = make_link(localhost, f"/web/rmanga/2/{path_segment_manga}/")
        chapter_link_server = make_link(
            localhost, f"/web/rmanga/2/{path_segment_manga}/{path_segment_chapter}/"
        )

        manga_detail = {
            "id_manga": id_manga,
            "title_manga": title_manga,
            "image_poster_link_goc": poster_manga,
            "description_manga": "",
            "path_segment_manga": path_segment_manga,
            "url_manga": manga_link_server,
            "chapter_new": title_chapter,
            "path_segment_chapter": path_segment_chapter,
            "url_chapter": chapter_link_server,
        }

        full_popular_manga.append(manga_detail)

    return full_popular_manga


def get_manga_server_2(path):
    link = f"https://www.mangareader.cc/manga/{path}"
    request_manga = requests.get(link)
    localhost = split_join(request.url)
    soup_manga = BeautifulSoup(request_manga.text, "html.parser")
    manga = soup_manga.find("div", {"id": "content"})
    manga_poster = manga.find("div", {"class": "imgdesc"}).find("img").get("src")

    # GET MANGA INFORMATION
    ListLI = soup_manga.find("div", {"class": "listinfo"}).select("li")
    try:
        author = ListLI[2].text.replace("Author:", "")
    except:
        author = ""
    try:
        status = ListLI[4].text.split()[1]
    except:
        status = ""
    try:
        categories = []
        for categoryIndex in ListLI[5].findAll("a"):
            categories.append(categoryIndex.text)
        categories = ", ".join(categories)
    except:
        categories = ""

    manga_title = ""
    try:
        manga_title = (
            manga.find("div", class_="rm").find("h1", {"itemprop": "name"}).text.strip()
        )
    except:
        pass

    description = ""
    try:
        description = (
            manga.find("div", {"id": "noidungm"}).text.replace("\n", "").strip()
        )
    except:
        pass

    chapters = {}
    chapters_name = []
    chapter_list = manga.find("div", {"class": "cl"}).find("ul")
    for chapter in chapter_list.find_all("span", class_="leftoff"):
        id_chapter = chapter.find("a").get("href")
        path_segment_chapter = id_chapter.split("/")[-1]
        chapter_title = chapter.find("a").get("title")
        chapter_title = chapter_title.replace(f"{manga_title} ", "")
        chapters_name.append(chapter_title)
        link_server = make_link(
            localhost, f"/web/rmanga/2/{path}/{path_segment_chapter}/"
        )
        chapters[f"{chapter_title}"] = link_server

    str_chapters_name = ", ".join(chapters_name)

    manga_info = {
        "genres": "manga",
        "id_manga": link,
        "title": manga_title,
        "description": description,
        "poster": manga_poster,
        "categories": categories,
        "status": status,
        "author": author,
        "chapters": chapters,
    }
    try:
        if check_manga(path):
            insertMangaIntoTable(
                link,
                "0",
                "5.0",
                description,
                manga_poster,
                link,
                str_chapters_name,
                author,
                categories,
                status,
                manga_title,
                "https://www.mangareader.cc",
                "",
            )
    except:
        pass

    return manga_info


def get_image_chapter_server_2(path, id_chapter):
    images = []
    id_manga = f"https://www.mangareader.cc/manga/{path}"
    link_chapter = f"https://www.mangareader.cc/chapter/{id_chapter}/"
    request = requests.get(link_chapter)
    soup_chapter = BeautifulSoup(request.text, "html.parser")
    # GET MANGA_TITLE, CHAPTER_TITLE

    chapter_title = (
        soup_chapter.find("div", {"id": "main"})
        .find("h1", {"class": "chapter-title"})
        .text
    )
    manga_title = (
        soup_chapter.find("div", {"id": "main"})
        .find("h2", {"class": "chapter-title"})
        .find("a")
        .get("title")
    )
    manga_title = manga_title.replace(" Manga", "")

    # GET IMAGES
    list_imgage = (
        soup_chapter.find("div", {"id": "readerarea"})
        .find("div", {"class": "chapter-content-inner text-center image-auto"})
        .find("p")
        .text
    )
    list_imgage = list_imgage.split(",")
    for image in list_imgage:
        images.append(image)

    chapter_info = {
        "title": manga_title,
        "image_chapter": images,
        "chapter_title": chapter_title,
    }

    try:
        if check_chapter(link_chapter):
            insertListChapter(link_chapter, chapter_title, id_chapter, id_manga)
    except:
        pass

    try:
        str_images = ", ".join(images)
        if check_image_chapter(path, id_chapter):
            insertImageChapter(f"{path}-{id_chapter}", link_chapter, "", str_images)
    except:
        pass

    return chapter_info


# NINEMANGA.COM
def get_lasted_manga_updates_server_3():
    session["server"] = 3
    full_latest_update = []
    link = "https://www.ninemanga.com/list/New-Update/"
    localhost = split_join(request.url)
    content = by_pass_data(link, 10)
    if content is None:
        return full_latest_update
    soup_home = BeautifulSoup(content, "html.parser")

    for latest_Update in soup_home.find_all("ul", class_="direlist"):
        for manga in latest_Update.find_all("li"):

            manga_link_original = manga.find("a").get("href")
            manga_link_original = urllib.parse.unquote(manga_link_original)
            manga_poster = manga.find("img").get("src")
            manga_title = manga.find("a", class_="bookname").text
            description_manga = manga.find("p").text
            chapter_link_original = manga.find("a", class_="chaptername").get("href")
            chapter = manga.find("a", class_="chaptername").text
            path_segment_manga = manga_link_original.split("/")[4]

            url = chapter_link_original.split("/")
            if len(url) == 5:
                continue
            path_segment_chapter = url[4]
            id_chapter = url[5]

            manga_link_server = make_link(
                localhost, f"/web/rmanga/3/{path_segment_manga}/"
            )
            chapter_link_server = make_link(
                localhost, f"/web/rmanga/3/{path_segment_chapter}/{id_chapter}/"
            )

            manga_detail = {
                "id_manga": manga_link_original,
                "title_manga": manga_title.replace("\n", ""),
                "image_poster_link_goc": manga_poster,
                "description_manga": description_manga,
                "path_segment_manga": path_segment_manga.replace(".html", ""),
                "url_manga": manga_link_server.replace(".html", ""),
                "chapter_new": chapter.replace("\n", ""),
                "path_segment_chapter": path_segment_chapter,
                "url_chapter": chapter_link_server.replace(".html", ""),
            }
            full_latest_update.append(manga_detail)
            # print("_______check_____", manga_title)
    return full_latest_update


def get_hot_manga_server_3():
    session["server"] = 3
    hot_manga = []
    link = "https://www.ninemanga.com/list/Hot-Book/"
    localhost = split_join(request.url)
    request_home = by_pass_data(link, 10)
    soup_home = BeautifulSoup(request_home, "html.parser")

    list_hot_manga = soup_home.find_all("div", class_="mainbox")[1]
    # print(list_hot_manga)
    for manga in list_hot_manga.find_all("dl", class_="bookinfo"):
        id_manga = ""
        try:
            id_manga = manga.find("dt").find("a").get("href")
            id_manga = urllib.parse.unquote(id_manga)
        except:
            pass

        manga_poster = ""
        try:
            manga_poster = manga.find("dt").find("a").find("img").get("src")
        except:
            pass

        manga_title = ""
        try:
            manga_title = manga.find("dd").find("a", class_="bookname").text.strip()
        except:
            pass

        description_manga = ""
        try:
            description_manga = manga.find("p").text
        except:
            pass

        id_chapter = ""
        try:
            id_chapter = manga.find("a", class_="chaptername").get("href")
        except:
            pass

        chapter_title = ""
        try:
            chapter_title = manga.find("a", class_="chaptername").text
        except:
            pass

        path_segment_manga = id_manga.split("/")[4]

        url = id_chapter.split("/")
        if len(url) == 5:
            continue
        path_segment_chapter = url[4]
        id_chapter = url[5]

        manga_link_server = make_link(localhost, f"/web/rmanga/3/{path_segment_manga}/")
        chapter_link_server = make_link(
            localhost, f"/web/rmanga/3/{path_segment_chapter}/{id_chapter}/"
        )

        manga_detail = {
            "id_manga": id_manga,
            "title_manga": manga_title.replace("\n", ""),
            "image_poster_link_goc": manga_poster,
            "description_manga": description_manga,
            "path_segment_manga": path_segment_manga.replace(".html", ""),
            "url_manga": manga_link_server.replace(".html", ""),
            "chapter_new": chapter_title.replace("\n", ""),
            "path_segment_chapter": path_segment_chapter,
            "url_chapter": chapter_link_server.replace(".html", ""),
        }
        hot_manga.append(manga_detail)
        # print("_______check_____", manga_title)
    return hot_manga


def get_manga_server_3(path):
    base_link = "https://www.ninemanga.com"
    # path = urllib.parse.quote(path, safe=':/')
    # print(path)
    link = f"https://www.ninemanga.com/manga/{path}.html?waring=1"
    id_manga = f"https://www.ninemanga.com/manga/{path}.html"
    request_manga = by_pass_data(link, 10)
    localhost = split_join(request.url)
    soup_manga = BeautifulSoup(request_manga, "html.parser")
    manga = soup_manga.find("div", class_="manga")

    manga_title = ""
    try:
        manga_title = manga.find("div", class_="ttline").find("h1").text.strip()
    except:
        pass

    manga_poster = ""
    try:
        manga_poster = manga.find("img").get("src")
    except:
        pass

    description = ""
    try:
        description = manga.find("p", itemprop="description").text.strip()
        description = description.split("\n")[2]
    except:
        pass

    cats = manga.find("li", itemprop="genre")
    try:
        categories = []
        for category in cats.find_all("a"):
            categories.append(category.text)
    except:
        pass

    status = ""
    try:
        status = manga.find("a", href="/category/updated.html").text.strip()
    except:
        pass

    author = ""
    try:
        author = manga.find("a", itemprop="author").text.strip()
    except:
        pass

    list_chapter = manga.find_all("a", class_="chapter_list_a")
    chapters = {}
    chapters_name = []
    for chapter in list_chapter:
        chapter_title = chapter.text.strip()
        chapters_name.append(chapter_title)
        original_link_chapter = chapter.get("href")
        url = original_link_chapter.split("/")
        path_segment_chapter = urllib.parse.unquote(url[4]).replace(" ", "+")
        id_chapter = url[5].replace(".html", "")
        chapter_link_server = make_link(
            localhost, f"/web/rmanga/3/{path_segment_chapter}/{id_chapter}/"
        )
        chapters[f"{chapter_title}"] = chapter_link_server

    str_chapters = ", ".join(chapters_name)
    str_categories = ", ".join(categories)

    manga_info = {
        "genres": "manga",
        "id_manga": id_manga,
        "title": manga_title,
        "description": description,
        "poster": manga_poster,
        "categories": str_categories,
        "status": status,
        "author": author,
        "chapters": chapters,
    }

    try:
        # print(check_manga(path))
        if check_manga(path):
            insertMangaIntoTable(
                id_manga,
                "0",
                "5.0",
                description,
                manga_poster,
                link,
                str_chapters,
                author,
                str_categories,
                status,
                manga_title,
                base_link,
                "",
            )
    except:
        pass

    return manga_info


def get_image_chapter_server_3(path, id_chapter):
    base_link = "https://www.ninemanga.com"
    images = []
    path = urllib.parse.quote(path)
    link_chapter = f"{base_link}/chapter/{path}/{id_chapter}"
    request = by_pass_data(f"{link_chapter}-10-1.html", 10)
    soup_chapter = BeautifulSoup(request, "html.parser")
    title_soup = soup_chapter.find("title").text

    # GET ID_MANGA
    tmp = soup_chapter.find("div", class_="subgiude").find_all("li")
    title_manga = tmp[1].find("a").text

    # Get path_segment manga
    path_segment_manga = urllib.parse.unquote(title_manga).replace(" ", "+")
    link_chapter_original = (
        f"https://www.ninemanga.com/chapter/{path_segment_manga}/{id_chapter}/"
    )

    id_manga = f"https://www.ninemanga.com/manga/{path_segment_manga}.html"
    # print(id_manga)

    title_chapter = title_soup.split("page")[0]
    selectchapter = soup_chapter.find("div", class_="changepage")

    indexchapterstr = selectchapter.find("option")
    if indexchapterstr is not None:
        indexchapterstrs = indexchapterstr.text
        # print(indexchapterstrs)
        indexchapters = indexchapterstrs[2:]
        # print(indexchapters)
        totalAllchapters = int(indexchapters)
        # print(indexchapters)

    for indexchapter in range(totalAllchapters):
        link_chapter_10 = link_chapter + "-10-" + str(indexchapter + 1) + ".html"
        request_All_link_chapter10 = by_pass_data(link_chapter_10, 4)
        # print(request_All_link_chapter10)
        soup_All_linkchapter_10 = BeautifulSoup(
            request_All_link_chapter10, "html.parser"
        )
        for image_All in soup_All_linkchapter_10.find_all("div", class_="pic_box"):
            for image in image_All.findAll("img"):
                x = image.get("src")
                # y = uploadImagetoImgbb(image.get('src'))
                images.append(x)
                # print(x)
                # backup.append(y)
    chapter_info = {
        "title": title_manga,
        "image_chapter": images,
        "chapter_title": title_chapter,
    }

    try:
        # print(check_chapter(link_chapter_original))
        # print(link_chapter_original, title_chapter, id_chapter, id_manga)
        if check_chapter(link_chapter_original):
            insertListChapter(
                link_chapter_original, title_chapter, id_chapter, id_manga
            )
    except:
        pass

    try:
        str_images = ",".join(images)
        # print(check_image_chapter(path_segment_manga, id_chapter))
        if check_image_chapter(path_segment_manga, id_chapter):
            insertImageChapter(
                f"{path_segment_manga}-{id_chapter}",
                f"https://www.ninemanga.com/chapter/{path_segment_manga}/{id_chapter}/",
                "",
                str_images,
            )
    except:
        pass

    return chapter_info


# MANGAKOMI
def get_lasted_manga_updates_server_6():
    base_link = "https://mangakomi.io/"
    session["server"] = 6
    full_latest_update = []
    localhost = split_join(request.url)
    link_lastest_update = "https://mangakomi.io/manga/?m_orderby=latest"
    request_home = requests.get(link_lastest_update)
    soup_home = BeautifulSoup(request_home.text, "html.parser")
    print(soup_home)
    lastest_update_mangas = soup_home.find("div", class_="tab-content-wrap")

    if lastest_update_mangas:
        for lastest_update in lastest_update_mangas.find_all(
            "div", {"class": "page-item-detail manga"}
        ):
            id_manga = lastest_update.find("a").get("href")
            manga_poster = lastest_update.find("img").get("data-src")
            manga_title = lastest_update.find("a").get("title")
            try:
                chapter_new = (
                    lastest_update.find("div", {"class": "list-chapter"})
                    .find("div", {"class": "chapter-item"})
                    .find_all("span")
                )
                id_chapter = chapter_new[0].find("a").get("href")
                chapter_title = chapter_new[0].find("a").text
                path_segment_chapter = id_chapter.split("/")[-2]
            except:
                id_chapter = ""
                chapter_title = ""
                path_segment_chapter = ""

            path_segment_manga = id_manga.split("/")[-2]

            manga_link_server = make_link(
                localhost, f"/web/rmanga/6/{path_segment_manga}/"
            )
            chapter_link_server = make_link(
                localhost, f"/web/rmanga/6/{path_segment_manga}/{path_segment_chapter}/"
            )

            manga_detail = {
                "id_manga": id_manga,
                "title_manga": manga_title,
                "image_poster_link_goc": manga_poster,
                "description_manga": "",
                "path_segment_manga": path_segment_manga,
                "url_manga": manga_link_server,
                "chapter_new": chapter_title,
                "path_segment_chapter": path_segment_chapter,
                "url_chapter": chapter_link_server,
            }
            full_latest_update.append(manga_detail)
    return full_latest_update


def get_manga_server_6(path):
    link = f"https://mangakomi.io/manga/{path}/"
    request_manga = requests.get(link)
    localhost = split_join(request.url)
    soup_manga = BeautifulSoup(request_manga.text, "html.parser")
    manga = soup_manga.find("div", class_="site-content")

    manga_title = ""
    try:
        manga_title = (
            manga.find("div", class_="post-title").text.replace("\n", "").strip()
        )
    except:
        pass

    manga_infomation = manga.find("div", class_="tab-summary")
    manga_poster = (
        manga_infomation.find("div", class_="summary_image").find("img").get("data-src")
    )

    categories = []

    str_categories = ""
    try:
        categories = [
            item.text
            for item in manga_infomation.find("div", class_="genres-content").find_all(
                "a"
            )
        ]
        str_categories = ", ".join(categories)
    except:
        pass

    status = (
        manga_infomation.find("div", class_="post-status")
        .find("div", class_="summary-content")
        .text.strip()
    )

    author = ""

    description = (
        manga.find("div", {"class": "summary__content show-more"})
        .find("p")
        .text.strip()
    )

    list_chapter = manga.find("ul", class_="main version-chap no-volumn").find_all(
        "li", class_="wp-manga-chapter"
    )
    chapters = {}
    chapters_name = []
    for chapter in list_chapter:
        link_chapter = chapter.find("a").get("href")
        chapter_title = chapter.find("a").text.strip()
        chapters_name.append(chapter_title)
        path_segment_chapter = link_chapter.split("/")[-2]
        chapter_link_server = make_link(
            localhost, f"/web/rmanga/6/{path}/{path_segment_chapter}/"
        )
        chapters[f"{chapter_title}"] = chapter_link_server

    str_chapters = ", ".join(chapters_name)

    manga_info = {
        "genres": "manga",
        "id_manga": link,
        "title": manga_title,
        "description": description,
        "poster": manga_poster,
        "categories": str_categories,
        "status": status,
        "author": author,
        "chapters": chapters,
    }

    try:
        if check_manga(path):
            insertMangaIntoTable(
                link,
                "0",
                "5.0",
                description,
                manga_poster,
                link,
                str_chapters,
                author,
                str_categories,
                status,
                manga_title,
                "https://mangakomi.io/manga/",
                "",
            )
    except:
        pass

    return manga_info


def get_image_chapter_server_6(path, id_chapter):
    images = []
    link_chapter = f"https://mangakomi.io/manga/{path}/{id_chapter}/"
    request = requests.get(link_chapter)
    soup_chapter = BeautifulSoup(request.text, "html.parser")

    manga_info = soup_chapter.find("div", {"class": "main-col-inner"})

    # GET ID_MANGA
    tmp = manga_info.find("ol", class_="breadcrumb").find_all("li")
    id_manga = tmp[2].find("a").get("href")
    title_manga = tmp[2].find("a").text
    title_manga = title_manga.replace("\n", "")

    # Get path_segment manga
    path_segment_manga = path

    title_chapter = tmp[-1].text
    title_chapter = title_chapter.replace("\n", "")

    list_image = soup_chapter.find("div", class_="reading-content")
    for image in list_image.find_all("img"):
        tmp_image = image.get("data-src")
        tmp_image = tmp_image.replace("\t", "").replace("\n", "")
        images.append(tmp_image)

    str_images = ",".join(images)

    chapter_info = {
        "title": title_manga,
        "image_chapter": images,
        "chapter_title": title_chapter,
    }

    try:
        if check_chapter(link_chapter):
            insertListChapter(
                link_chapter,
                title_chapter,
                id_chapter,
                id_manga,
            )
    except:
        pass

    try:
        str_images = ",".join(images)
        if check_image_chapter(path_segment_manga, id_chapter):
            insertImageChapter(
                f"{path_segment_manga}-{id_chapter}", link_chapter, "", str_images
            )
    except:
        pass

    return chapter_info


# READM
def get_lasted_manga_updates_server_7():
    base_link = "https://readm.org"
    session["server"] = 7
    full_latest_update = []
    localhost = split_join(request.url)
    link_lastest_update = "https://readm.org/latest-releases"
    request_home = requests.get(link_lastest_update)
    soup_home = BeautifulSoup(request_home.text, "html.parser")

    lastest_update = soup_home.find("div", class_="dark-segment")
    for manga in lastest_update.find_all("li", class_="segment-poster-sm"):
        id_manga = base_link + manga.find("div", class_="poster-subject").find(
            "h2", class_="truncate"
        ).find("a").get("href")
        manga_title = ""
        try:
            manga_title = (
                manga.find("div", class_="poster-subject")
                .find("h2", class_="truncate")
                .find("a")
                .text
            )
        except:
            pass
        path_segment_manga = ""
        try:
            path_segment_manga = id_manga.split("/")[-1]
        except:
            pass

        chapter_new = manga.find("ul", class_="chapters").find("a")

        id_chapter = ""
        try:
            id_chapter = chapter_new.get("href")
        except:
            pass

        chapter_title = ""
        try:
            chapter_title = chapter_new.text
        except:
            pass

        path_segment_chapter = ""
        try:
            path_segment_chapter = id_chapter.split("/")[-1]
        except:
            pass

        manga_poster = ""
        try:
            manga_poster = base_link + manga.find("img").get("data-src")
        except:
            pass

        manga_link_server = make_link(localhost, f"/web/rmanga/7/{path_segment_manga}/")
        chapter_link_server = make_link(
            localhost, f"/web/rmanga/7/{path_segment_manga}/{path_segment_chapter}/"
        )

        manga_detail = {
            "id_manga": id_manga,
            "title_manga": manga_title,
            "image_poster_link_goc": manga_poster,
            "description_manga": "",
            "path_segment_manga": path_segment_manga,
            "url_manga": manga_link_server,
            "chapter_new": chapter_title,
            "path_segment_chapter": path_segment_chapter,
            "url_chapter": chapter_link_server,
        }
        full_latest_update.append(manga_detail)

    return full_latest_update


def get_manga_server_7(path):
    base_link = "https://readm.org"
    link = f"https://readm.org/manga/{path}"
    request_manga = requests.get(link)
    localhost = split_join(request.url)
    soup_manga = BeautifulSoup(request_manga.text, "html.parser")
    manga = soup_manga.find("div", {"id": "content"})

    manga_title = (
        manga.find(
            "div",
            {"class": "left floated sixteen wide tablet eight wide computer column"},
        )
        .find("h1")
        .text
    )
    manga_infomation = manga.find(
        "div", {"class": "item", "id": "series-profile-wrapper"}
    )
    manga_poster = base_link + manga_infomation.find("a", class_="ui image").find(
        "img"
    ).get("src")

    list_catergories = manga_infomation.find_all("div", class_="ui list", limit=1)
    categories = []
    str_categories = ""
    try:
        categories = [item.text for item in list_catergories[0].find_all("a")]
        str_categories = ", ".join(categories)
    except:
        str_categories = ""

    status = ""
    try:
        status = manga.find("span", class_="series-status aqua").text
    except:
        pass

    author = ""
    try:
        author = manga_infomation.find("div", class_="first_and_last").find("a").text
    except:
        pass

    description = ""
    try:
        description = (
            manga_infomation.find("div", {"class": "series-summary-wrapper"})
            .find("span")
            .text
        )
    except:
        pass

    list_chapter = manga.find(
        "div", class_="sixteen wide tablet eleven wide computer column"
    ).find_all("div", class_="item season_start")
    chapters = {}
    chapters_name = []
    for chapter in list_chapter:
        link_chapter = (
            chapter.find(
                "td", {"id": "table-episodes-title", "class": "table-episodes-title"}
            )
            .find("h6")
            .find("a")
            .get("href")
        )
        chapter_title = (
            chapter.find(
                "td", {"id": "table-episodes-title", "class": "table-episodes-title"}
            )
            .find("h6")
            .find("a")
            .text.strip()
        )
        chapters_name.append(chapter_title)
        path_segment_chapter = link_chapter.split("/")[-2]
        chapter_link_server = make_link(
            localhost, f"/web/rmanga/7/{path}/{path_segment_chapter}/"
        )
        chapters[f"{chapter_title}"] = chapter_link_server

    str_chapters = ", ".join(chapters_name)

    manga_info = {
        "genres": "manga",
        "id_manga": link,
        "title": manga_title,
        "description": description,
        "poster": manga_poster,
        "categories": str_categories,
        "status": status,
        "author": author,
        "chapters": chapters,
    }

    try:
        if check_manga(path):
            insertMangaIntoTable(
                link,
                "0",
                "5.0",
                description,
                manga_poster,
                link,
                str_chapters,
                author,
                str_categories,
                status,
                manga_title,
                base_link,
                "",
            )
    except:
        pass

    return manga_info


def get_image_chapter_server_7(path, id_chapter):
    base_link = "https://readm.org"
    images = []
    link_chapter = f"https://readm.org/manga/{path}/{id_chapter}/all-pages"
    request = requests.get(link_chapter)
    soup_chapter = BeautifulSoup(request.text, "html.parser")

    manga_info = soup_chapter.find("div", {"class": "ui grid"})

    # GET ID_MANGA
    id_manga = base_link + manga_info.find("span").find("a").get("href")
    title_manga = manga_info.find("span").find("a").text
    title_manga = title_manga.replace("\n", "").strip()

    # Get path_segment manga
    path_segment_manga = path

    title_chapter = (
        manga_info.find(
            "div", class_="ui secondary dropdown top left pointing selection"
        )
        .find("div", class_="text")
        .text
    )
    title_chapter = title_chapter.replace("\n", "")

    list_image = soup_chapter.find("div", class_="ch-images ch-image-container")
    for image in list_image.find_all("img"):
        tmp_image = base_link + image.get("src")
        images.append(tmp_image)
    str_images = ",".join(images)

    chapter_info = {
        "title": title_manga,
        "image_chapter": images,
        "chapter_title": title_chapter,
    }

    try:
        if check_chapter(link_chapter):
            insertListChapter(
                link_chapter,
                title_chapter,
                id_chapter,
                id_manga,
            )
    except:
        pass

    try:
        str_images = ",".join(images)
        if check_image_chapter(path_segment_manga, id_chapter):
            insertImageChapter(
                f"{path_segment_manga}-{id_chapter}",
                f"{base_link}/manga/{path_segment_manga}/{id_chapter}/",
                "",
                str_images,
            )
    except:
        pass

    return chapter_info


# SWATMANGA
def get_lasted_manga_updates_server_9():
    base_link = "https://swatmanga.net"
    session["server"] = 9
    full_latest_update = []
    localhost = split_join(request.url)
    link_lastest_update = "https://swatmanhua.com/"
    request_home = requests.get(link_lastest_update)
    soup_home = BeautifulSoup(request_home.text, "html.parser")

    lastest_update = soup_home.find("div", class_="d-flex container-content-sidebar")
    for manga in lastest_update.find_all("div", class_="utao"):
        id_manga = manga.find("div", class_="imgu").find("a").get("href")
        manga_title = manga.find("div", class_="imgu").find("a").get("title")
        path_segment_manga = id_manga.split("/")[-1]

        chapter_new = manga.find("div", class_="luf").find("ul", class_="manhua")
        if chapter_new is None:
            chapter_new = manga.find("div", class_="luf").find("ul", class_="manhwa")
        if chapter_new is None:
            chapter_new = manga.find("div", class_="luf").find("ul", class_="manga")
        chapter_new = chapter_new.find_all("li", limit=1)

        id_chapter = chapter_new[0].find("a").get("href")
        chapter_title = chapter_new[0].find("a").text
        chapter_title = chapter_title.replace(" FREE", "")
        path_segment_chapter = id_chapter.split("/")[-1]

        manga_poster = manga.find("img").get("data-lazy-src")

        manga_link_server = make_link(localhost, f"/web/rmanga/9/{path_segment_manga}/")
        chapter_link_server = make_link(
            localhost, f"/web/rmanga/9/{path_segment_manga}/{path_segment_chapter}/"
        )

        manga_detail = {
            "id_manga": id_manga,
            "title_manga": manga_title,
            "image_poster_link_goc": manga_poster,
            "description_manga": "",
            "path_segment_manga": path_segment_manga,
            "url_manga": manga_link_server,
            "chapter_new": chapter_title,
            "path_segment_chapter": path_segment_chapter,
            "url_chapter": chapter_link_server,
        }
        full_latest_update.append(manga_detail)

    return full_latest_update


def get_manga_server_9(path):
    base_link = "https://swatmanga.net"
    link = f"https://swatmanhua.com/manga/{path}"
    request_manga = requests.get(link)
    localhost = split_join(request.url)
    soup_manga = BeautifulSoup(request_manga.text, "html.parser")
    manga = soup_manga.find("article", {"itemscope": "itemscope"})

    manga_infomation = manga.find("div", {"class": "bigcontent"}).find(
        "div", class_="infox"
    )
    manga_title = manga_infomation.find("h1").text
    manga_poster = ""
    try:
        manga_poster = (
            manga.find("div", {"class": "thumb", "itemprop": "image"})
            .find("img")
            .get("data-lazy-src")
        )
    except:
        pass

    tmp = manga_infomation.find("div", class_="spe").find_all("span")
    list_catergories = tmp[0]
    categories = []
    str_categories = ""
    try:
        categories = [item.text for item in list_catergories.find_all("a")]
        str_categories = ", ".join(categories)
    except:
        str_categories = ""

    status = ""
    try:
        status = tmp[1].find("a").text
    except:
        pass

    author = ""
    try:
        author = tmp[3].find("i").text
    except:
        pass

    description = ""
    try:
        description = manga_infomation.find("div", {"class": "desc"}).find("p").text
    except:
        pass

    list_chapter = manga.find("div", class_="bixbox bxcl").find_all("li")
    chapters = {}
    chapters_name = []
    for chapter in list_chapter:
        chapter_info = chapter.find_all("span")
        link_chapter = chapter_info[0].find("a").get("href")
        chapter_title = chapter_info[2].find("span").text.replace(" FREE", "")
        chapters_name.append(chapter_title)
        path_segment_chapter = link_chapter.split("/")[-1]
        chapter_link_server = make_link(
            localhost, f"/web/rmanga/9/{path}/{path_segment_chapter}/"
        )
        chapters[f"{chapter_title}"] = chapter_link_server

    str_chapters = ", ".join(chapters_name)

    manga_info = {
        "genres": "manga",
        "id_manga": link,
        "title": manga_title,
        "description": description,
        "poster": manga_poster,
        "categories": str_categories,
        "status": status,
        "author": author,
        "chapters": chapters,
    }

    try:
        if check_manga(path):
            insertMangaIntoTable(
                link,
                "0",
                "5.0",
                description,
                manga_poster,
                link,
                str_chapters,
                author,
                str_categories,
                status,
                manga_title,
                base_link,
                "",
            )
    except:
        pass

    return manga_info


def get_image_chapter_server_9(path, id_chapter):
    base_link = 'base_link = "https://swatmanga.net"'
    images = []
    link_chapter = f"https://swatmanhua.com/manga/{path}/{id_chapter}"
    request = requests.get(link_chapter)
    soup_chapter = BeautifulSoup(request.text, "html.parser")

    manga_info = soup_chapter.find("div", {"id": "content", "class": "readercontent"})

    # GET ID_MANGA
    id_manga = manga_info.find("div", class_="allc").find("a").get("href")
    title_manga = manga_info.find("div", class_="allc").find("a").text
    title_manga = title_manga.replace("\n", "").strip()

    # Get path_segment manga
    path_segment_manga = path

    title_chapter = manga_info.find("div", class_="headpost").find("h1").text
    title_chapter = title_chapter.replace("\n", "")

    try:
        script_list = soup_chapter.find_all("script")
        list_img = script_list[-4].text
        json_str = re.search(r"ts_reader.run\((\{.*?\})\);", list_img, re.DOTALL).group(
            1
        )
        data = json.loads(json_str)
        for image in data["sources"][0]["images"]:
            images.append(image)
        str_images = ",".join(images)
    except:
        pass

    chapter_info = {
        "title": title_manga,
        "image_chapter": images,
        "chapter_title": title_chapter,
    }

    try:
        if check_chapter(link_chapter):
            insertListChapter(
                link_chapter,
                title_chapter,
                id_chapter,
                id_manga,
            )
    except:
        pass

    try:
        str_images = ",".join(images)
        if check_image_chapter(path_segment_manga, id_chapter):
            insertImageChapter(
                f"{path_segment_manga}-{id_chapter}",
                f"{base_link}/manga/{path_segment_manga}/{id_chapter}/",
                "",
                str_images,
            )
    except:
        pass

    return chapter_info


# MTO
def get_lasted_manga_updates_server_12():
    base_link = "https://mto.to"
    session["server"] = 12
    full_latest_update = []
    localhost = split_join(request.url)
    link_lastest_update = "https://mto.to/latest?langs=en"
    request_home = requests.get(link_lastest_update)
    soup_home = BeautifulSoup(request_home.text, "html.parser")

    lastest_update = soup_home.find("div", {"id": "mainer", "class": "mainer"})
    for manga in lastest_update.find_all("div", class_="col item line-b no-flag"):
        id_manga = base_link + manga.find("a", class_="item-cover").get("href")
        manga_title = manga.find("a", class_="item-title").text
        path_segment_manga = id_manga.split("/")[-2]

        id_chapter = base_link + manga.find("div", class_="item-volch").find("a").get(
            "href"
        )
        chapter_title = manga.find("div", class_="item-volch").find("a").text
        path_segment_chapter = id_chapter.split("/")[-1]

        manga_poster = manga.find("img").get("src")

        manga_link_server = make_link(
            localhost, f"/web/rmanga/12/{path_segment_manga}/"
        )
        chapter_link_server = make_link(
            localhost, f"/web/rmanga/12/{path_segment_manga}/{path_segment_chapter}/"
        )

        manga_detail = {
            "id_manga": id_manga,
            "title_manga": manga_title,
            "image_poster_link_goc": manga_poster,
            "description_manga": "",
            "path_segment_manga": path_segment_manga,
            "url_manga": manga_link_server,
            "chapter_new": chapter_title,
            "path_segment_chapter": path_segment_chapter,
            "url_chapter": chapter_link_server,
        }
        full_latest_update.append(manga_detail)

    return full_latest_update


def get_popular_manga_server_12():
    base_link = "https://mto.to"
    session["server"] = 12
    full_popular_manga = []
    localhost = split_join(request.url)
    request_home = requests.get(base_link)
    soup_home = BeautifulSoup(request_home.text, "html.parser")

    popular_mangas = soup_home.find(
        "div", class_="mt-4 row row-cols-3 row-cols-md-4 row-cols-lg-8 g-0 home-popular"
    )
    for manga in popular_mangas.find_all("div", class_="col item"):
        id_manga = ""
        try:
            id_manga = base_link + manga.find("a", class_="item-cover").get("href")
        except:
            pass

        title_manga = ""
        try:
            title_manga = manga.find("a", class_="item-title").text
        except:
            pass

        poster_manga = ""
        try:
            poster_manga = manga.find("img").get("src")
        except:
            pass

        id_chapter = ""
        try:
            id_chapter = base_link + manga.find("a", class_="item-volch").get("href")
        except:
            pass

        title_chapter = ""
        try:
            title_chapter = manga.find("a", class_="item-volch").text
        except:
            pass

        path_segment_manga = id_manga.split("/")[-2]
        path_segment_chapter = id_chapter.split("/")[-1]

        manga_link_server = make_link(
            localhost, f"/web/rmanga/12/{path_segment_manga}/"
        )
        chapter_link_server = make_link(
            localhost, f"/web/rmanga/12/{path_segment_manga}/{path_segment_chapter}/"
        )

        manga_detail = {
            "id_manga": id_manga,
            "title_manga": title_manga,
            "image_poster_link_goc": poster_manga,
            "description_manga": "",
            "path_segment_manga": path_segment_manga,
            "url_manga": manga_link_server,
            "chapter_new": title_chapter,
            "path_segment_chapter": path_segment_chapter,
            "url_chapter": chapter_link_server,
        }

        full_popular_manga.append(manga_detail)

    return full_popular_manga


def get_manga_server_12(path):
    base_link = "https://mto.to"
    link = f"https://mto.to/series/{path}/"
    request_manga = requests.get(link)
    localhost = split_join(request.url)
    soup_manga = BeautifulSoup(request_manga.text, "html.parser")
    manga = soup_manga.find("div", {"id": "mainer", "class": "mainer"})

    manga_title = ""
    try:
        manga_title = manga.find("h3", class_="item-title").find("a").text.strip()
    except:
        pass

    id_manga = link

    manga_poster = ""
    try:
        manga_poster = (
            manga.find("div", class_="col-24 col-sm-8 col-md-6 attr-cover")
            .find("img")
            .get("src")
        )
    except:
        pass

    manga_infomation = manga.find(
        "div", class_="col-24 col-sm-16 col-md-18 mt-4 mt-sm-0 attr-main"
    ).find_all("div", class_="attr-item")

    categories = []
    str_categories = ""
    try:
        categories = [
            re.sub("\s+", " ", item.text).strip()
            for item in manga_infomation[3].find_all("span")
        ]
        str_categories = ", ".join(categories)
    except:
        pass

    status = ""
    try:
        status = manga_infomation[-1].find("span").text
    except:
        pass

    author = ""
    try:
        author = [item.text for item in manga_infomation[1].find_all("a")]
        author = ", ".join(author)
    except:
        pass

    description = ""
    try:
        description = (
            manga.find("div", {"class": "mt-3"})
            .find("div", class_="limit-html")
            .text.strip()
        )
    except:
        pass

    list_chapter = manga.find("div", class_="main").find_all(
        "div", class_="p-2 d-flex flex-column flex-md-row item is-new"
    )
    chapters = {}
    chapters_name = []
    for chapter in list_chapter:
        link_chapter = base_link + chapter.find("a", class_="visited chapt").get("href")
        chapter_title = (
            chapter.find("a", class_="visited chapt").text.replace("\n", "").strip()
        )
        chapters_name.append(chapter.find("a", class_="visited chapt").text)
        path_segment_chapter = link_chapter.split("/")[-1]
        chapter_link_server = make_link(
            localhost, f"/web/rmanga/12/{path}/{path_segment_chapter}/"
        )
        chapters[f"{chapter_title}"] = chapter_link_server

    list_chapter = manga.find("div", class_="main").find_all(
        "div", class_="p-2 d-flex flex-column flex-md-row item"
    )
    for chapter in list_chapter:
        link_chapter = base_link + chapter.find("a", class_="visited chapt").get("href")
        chapter_title = (
            chapter.find("a", class_="visited chapt").text.replace("\n", "").strip()
        )
        chapters_name.append(chapter_title)
        path_segment_chapter = link_chapter.split("/")[-1]
        chapter_link_server = make_link(
            localhost, f"/web/rmanga/{path}/{path_segment_chapter}/"
        )
        chapters[f"{chapter_title}"] = chapter_link_server

    str_chapters = ", ".join(chapters_name)

    manga_info = {
        "genres": "manga",
        "id_manga": id_manga,
        "title": manga_title,
        "description": description,
        "poster": manga_poster,
        "categories": str_categories,
        "status": status,
        "author": author,
        "chapters": chapters,
    }

    try:
        if check_manga(path):
            insertMangaIntoTable(
                link,
                "0",
                "5.0",
                description,
                manga_poster,
                link,
                str_chapters,
                author,
                str_categories,
                status,
                manga_title,
                base_link,
                "",
            )
    except:
        pass

    return manga_info


def get_image_chapter_server_12(path, id_chapter):
    base_link = "https://mto.to"
    images = []
    link_chapter = f"https://mto.to/chapter/{id_chapter}    "
    request = requests.get(link_chapter)
    soup_chapter = BeautifulSoup(request.text, "html.parser")
    manga_info = soup_chapter.find(
        "div",
        {
            "class": "container-fluid container-max-width-xl episode-nav top",
            "id": "container",
        },
    )

    # GET ID_MANGA
    id_manga = base_link + manga_info.find("h3").find("a").get("href")
    title_manga = manga_info.find("h3").find("a").text
    title_manga = title_manga.replace("\n", "").strip()

    # Get path_segment manga
    path_segment_manga = path

    title_chapter = ""
    try:
        list_script = soup_chapter.find_all("script")
        pattern = r"https?://(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(?:/[^/#?]+)+\.(?:jpg|jpeg|gif|png)"
        for image in re.findall(pattern, list_script[-7].text):
            images.append(image)

        pattern = r"const local_text_epi = '([^']+)'"
        match = re.search(pattern, list_script[-7].text)
        if match:
            title_chapter = match.group(1)
        else:
            pass
        title_chapter = title_chapter.replace("\n", "")
    except:
        pass

    str_images = ",".join(images)

    chapter_info = {
        "title": title_manga,
        "image_chapter": images,
        "chapter_title": title_chapter,
    }

    try:
        if check_chapter(link_chapter):
            insertListChapter(link_chapter, title_chapter, id_chapter, id_manga)
    except:
        pass

    try:
        str_images = ",".join(images)
        if check_image_chapter(path_segment_manga, id_chapter):
            insertImageChapter(
                f"{path_segment_manga}-{id_chapter}", link_chapter, "", str_images
            )
    except:
        pass

    return chapter_info


# DE.NINEMANGA
def get_lasted_manga_updates_server_13():
    base_link = "https://de.ninemanga.com"
    session["server"] = 13
    full_latest_update = []
    link = "https://de.ninemanga.com/list/New-Update/"

    localhost = split_join(request.url)
    request_home = by_pass_data(link, 10)
    soup_home = BeautifulSoup(request_home, "html.parser")

    for latest_Update in soup_home.find_all("ul", class_="direlist"):
        for manga in latest_Update.find_all("li"):

            manga_link_original = manga.find("a").get("href")
            manga_poster = manga.find("img").get("src")
            manga_title = manga.find("a", class_="bookname").text
            if manga_title == "":
                continue
            description_manga = manga.find("p").text
            chapter_link_original = manga.find("a", class_="chaptername").get("href")
            chapter = manga.find("a", class_="chaptername").text
            path_segment_manga = manga_link_original.split("/")[4]

            url = chapter_link_original.split("/")
            if len(url) == 5:
                continue
            path_segment_chapter = url[4]
            id_chapter = url[5]

            manga_link_server = make_link(
                localhost, f"/web/rmanga/13/{path_segment_manga}/"
            )
            chapter_link_server = make_link(
                localhost, f"/web/rmanga/13/{path_segment_chapter}/{id_chapter}/"
            )

            manga_detail = {
                "id_manga": manga_link_original,
                "title_manga": manga_title.replace("\n", ""),
                "image_poster_link_goc": manga_poster,
                "description_manga": description_manga,
                "path_segment_manga": path_segment_manga.replace(".html", ""),
                "url_manga": manga_link_server.replace(".html", ""),
                "chapter_new": chapter.replace("\n", ""),
                "path_segment_chapter": path_segment_chapter,
                "url_chapter": chapter_link_server.replace(".html", ""),
            }
            full_latest_update.append(manga_detail)
    return full_latest_update


def get_hot_manga_server_13():
    base_link = "https://de.ninemanga.com"
    session["server"] = 13
    hot_manga = []
    link = "https://de.ninemanga.com/list/Hot-Book/"

    localhost = split_join(request.url)
    request_home = by_pass_data(link, 10)
    soup_home = BeautifulSoup(request_home, "html.parser")

    list_hot_manga = soup_home.find_all("div", class_="mainbox")[1]
    # print(list_hot_manga)
    for manga in list_hot_manga.find_all("dl", class_="bookinfo"):
        id_manga = ""
        try:
            id_manga = manga.find("dt").find("a").get("href")
        except:
            pass

        manga_poster = ""
        try:
            manga_poster = manga.find("dt").find("a").find("img").get("src")
        except:
            pass

        manga_title = ""
        try:
            manga_title = manga.find("dd").find("a", class_="bookname").text.strip()
        except:
            pass

        description_manga = ""
        try:
            description_manga = manga.find("p").text
        except:
            pass

        id_chapter = ""
        try:
            id_chapter = manga.find("a", class_="chaptername").get("href")
        except:
            pass

        chapter_title = ""
        try:
            chapter_title = manga.find("a", class_="chaptername").text
        except:
            pass

        path_segment_manga = id_manga.split("/")[4]

        url = id_chapter.split("/")
        if len(url) == 5:
            continue
        path_segment_chapter = url[4]
        id_chapter = url[5]

        manga_link_server = make_link(
            localhost, f"/web/rmanga/13/{path_segment_manga}/"
        )
        chapter_link_server = make_link(
            localhost, f"/web/rmanga/13/{path_segment_chapter}/{id_chapter}/"
        )

        manga_detail = {
            "id_manga": id_manga,
            "title_manga": manga_title.replace("\n", ""),
            "image_poster_link_goc": manga_poster,
            "description_manga": description_manga,
            "path_segment_manga": path_segment_manga.replace(".html", ""),
            "url_manga": manga_link_server.replace(".html", ""),
            "chapter_new": chapter_title.replace("\n", ""),
            "path_segment_chapter": path_segment_chapter,
            "url_chapter": chapter_link_server.replace(".html", ""),
        }
        hot_manga.append(manga_detail)
        # print("_______check_____", manga_title)
    return hot_manga


def get_manga_server_13(path):
    base_link = "https://de.ninemanga.com"
    link = f"https://de.ninemanga.com/manga/{path}.html?waring=1"
    print("___SONPIPI________get_manga_server_13____" + str(link))
    id_manga = f"https://de.ninemanga.com/manga/{path}.html"
    request_manga = by_pass_data(link, 10)
    localhost = split_join(request.url)
    soup_manga = BeautifulSoup(request_manga, "html.parser")
    manga = soup_manga.find("div", class_="manga")

    manga_title = manga.find("div", class_="ttline").text
    if manga_title:
        manga_title = manga.find("div", class_="ttline").find("h1").text
    else:
        manga_title = ""

    manga_poster = ""
    try:
        manga_poster = manga.find("img").get("src")
    except:
        pass

    description = ""
    try:
        description = (
            manga.find("p", itemprop="description").text.replace("\n", "").strip()
        )
    except:
        pass

    cats = manga.find("li", itemprop="genre")
    try:
        categories = []
        for category in cats.find_all("a"):
            categories.append(category.text)
    except:
        pass

    status = ""
    try:
        status = manga.find("a", href="/category/updated.html").text
    except:
        pass

    author = ""
    try:
        author = manga.find("a", itemprop="author").text
    except:
        pass

    list_chapter = manga.find_all("a", class_="chapter_list_a")
    chapters = {}
    chapters_name = []
    for chapter in list_chapter:
        chapter_title = chapter.text
        chapters_name.append(chapter_title)
        original_link_chapter = chapter.get("href")
        url = original_link_chapter.split("/")
        path_segment_chapter = url[4]
        id_chapter = url[5].replace(".html", "")
        chapter_link_server = make_link(
            localhost, f"/web/rmanga/13/{path_segment_chapter}/{id_chapter}/"
        )
        chapters[f"{chapter_title}"] = chapter_link_server

    str_chapters = ", ".join(chapters_name)
    str_categories = ", ".join(categories)

    manga_info = {
        "genres": "manga",
        "id_manga": id_manga,
        "title": manga_title,
        "description": description,
        "poster": manga_poster,
        "categories": str_categories,
        "status": status,
        "author": author,
        "chapters": chapters,
    }

    try:
        if check_manga(path):
            insertMangaIntoTable(
                id_manga,
                "0",
                "5.0",
                description,
                manga_poster,
                link,
                str_chapters,
                author,
                str_categories,
                status,
                manga_title,
                base_link,
                "",
            )
    except:
        pass

    return manga_info


def get_image_chapter_server_13(path, id_chapter):
    base_link = "https://de.ninemanga.com"
    images = []
    path = urllib.parse.quote(path)
    link_chapter = f"{base_link}/chapter/{path}/{id_chapter}"
    request = by_pass_data(f"{link_chapter}-10-1.html", 10)
    # print(request)
    soup_chapter = BeautifulSoup(request, "html.parser")

    # GET ID_MANGA
    tmp = soup_chapter.find("div", class_="subgiude").find_all("li")
    id_manga = base_link + tmp[1].find("a").text
    title_manga = tmp[1].find("a").text

    # Get path_segment manga
    path_segment_manga = urllib.parse.quote_plus(title_manga)

    link_chapter_original = f"{base_link}/chapter/{path_segment_manga}/{id_chapter}/"

    title_chapter = (
        soup_chapter.find("div", class_="tip").find_all("a", limit=1)[0].text
    )
    selectchapter = soup_chapter.find("div", class_="changepage")

    indexchapterstr = selectchapter.find("option")
    # print(indexchapterstr)
    if indexchapterstr is not None:
        indexchapterstrs = indexchapterstr.text
        # print(indexchapterstrs)
        indexchapters = indexchapterstrs[2:]
        totalAllchapters = int(indexchapters)
        # print(totalAllchapters)

    for indexchapter in range(totalAllchapters):
        link_chapter_10 = link_chapter + "-10-" + str(indexchapter + 1) + ".html"
        request_All_link_chapter10 = by_pass_data(link_chapter_10, 5)
        # print(request_All_link_chapter10)
        soup_All_linkchapter_10 = BeautifulSoup(
            request_All_link_chapter10, "html.parser"
        )
        for image_All in soup_All_linkchapter_10.find_all("div", class_="pic_box"):
            for image in image_All.findAll("img"):
                x = image.get("src")
                # y = uploadImagetoImgbb(image.get('src'))
                images.append(x)
                # print(x)
                # backup.append(y)
    chapter_info = {
        "title": title_manga,
        "image_chapter": images,
        "chapter_title": title_chapter,
    }

    try:
        if check_chapter(link_chapter):
            insertListChapter(
                link_chapter_original, title_chapter, id_chapter, id_manga
            )
    except:
        pass

    try:
        str_images = ",".join(images)
        if check_image_chapter(path_segment_manga, id_chapter):
            insertImageChapter(
                f"{path_segment_manga}-{id_chapter}",
                f"{base_link}/chapter/{path_segment_manga}/{id_chapter}/",
                "",
                str_images,
            )
    except:
        pass

    return chapter_info


# BR.NINEMANGA
def get_lasted_manga_updates_server_14():
    base_link = "https://br.ninemanga.com"
    session["server"] = 14
    full_latest_update = []
    link = "https://br.ninemanga.com/list/New-Update/"

    localhost = split_join(request.url)
    request_home = by_pass_data(link, 10)
    soup_home = BeautifulSoup(request_home, "html.parser")

    for latest_Update in soup_home.find_all("ul", class_="direlist"):
        for manga in latest_Update.find_all("li"):

            manga_link_original = manga.find("a").get("href")
            manga_poster = manga.find("img").get("src")
            manga_title = manga.find("a", class_="bookname").text
            if manga_title == "":
                continue
            description_manga = manga.find("p").text
            chapter_link_original = manga.find("a", class_="chaptername").get("href")
            chapter = manga.find("a", class_="chaptername").text
            path_segment_manga = manga_link_original.split("/")[4]

            url = chapter_link_original.split("/")
            if len(url) == 5:
                continue
            path_segment_chapter = url[4]
            id_chapter = url[5]

            manga_link_server = make_link(
                localhost, f"/web/rmanga/14/{path_segment_manga}/"
            )
            chapter_link_server = make_link(
                localhost, f"/web/rmanga/14/{path_segment_chapter}/{id_chapter}/"
            )

            manga_detail = {
                "id_manga": manga_link_original,
                "title_manga": manga_title.replace("\n", ""),
                "image_poster_link_goc": manga_poster,
                "description_manga": description_manga,
                "path_segment_manga": path_segment_manga.replace(".html", ""),
                "url_manga": manga_link_server.replace(".html", ""),
                "chapter_new": chapter.replace("\n", ""),
                "path_segment_chapter": path_segment_chapter,
                "url_chapter": chapter_link_server.replace(".html", ""),
            }
            full_latest_update.append(manga_detail)
    return full_latest_update


def get_hot_manga_server_14():
    base_link = "https://br.ninemanga.com"
    session["server"] = 14
    hot_manga = []
    link = "https://br.ninemanga.com/list/Hot-Book/"

    localhost = split_join(request.url)
    request_home = by_pass_data(link, 10)
    soup_home = BeautifulSoup(request_home, "html.parser")

    list_hot_manga = soup_home.find_all("div", class_="mainbox")[1]
    # print(list_hot_manga)
    for manga in list_hot_manga.find_all("dl", class_="bookinfo"):
        id_manga = ""
        try:
            id_manga = manga.find("dt").find("a").get("href")
        except:
            pass

        manga_poster = ""
        try:
            manga_poster = manga.find("dt").find("a").find("img").get("src")
        except:
            pass

        manga_title = ""
        try:
            manga_title = manga.find("dd").find("a", class_="bookname").text.strip()
        except:
            pass

        description_manga = ""
        try:
            description_manga = manga.find("p").text
        except:
            pass

        id_chapter = ""
        try:
            id_chapter = manga.find("a", class_="chaptername").get("href")
        except:
            pass

        chapter_title = ""
        try:
            chapter_title = manga.find("a", class_="chaptername").text
        except:
            pass

        path_segment_manga = id_manga.split("/")[4]

        url = id_chapter.split("/")
        if len(url) == 5:
            continue
        path_segment_chapter = url[4]
        id_chapter = url[5]

        manga_link_server = make_link(
            localhost, f"/web/rmanga/14/{path_segment_manga}/"
        )
        chapter_link_server = make_link(
            localhost, f"/web/rmanga/14/{path_segment_chapter}/{id_chapter}/"
        )

        manga_detail = {
            "id_manga": id_manga,
            "title_manga": manga_title.replace("\n", ""),
            "image_poster_link_goc": manga_poster,
            "description_manga": description_manga,
            "path_segment_manga": path_segment_manga.replace(".html", ""),
            "url_manga": manga_link_server.replace(".html", ""),
            "chapter_new": chapter_title.replace("\n", ""),
            "path_segment_chapter": path_segment_chapter,
            "url_chapter": chapter_link_server.replace(".html", ""),
        }
        hot_manga.append(manga_detail)
        # print("_______check_____", manga_title)
    return hot_manga


def get_manga_server_14(path):
    base_link = "https://br.ninemanga.com"
    link = f"https://br.ninemanga.com/manga/{path}.html?waring=1"
    id_manga = f"https://br.ninemanga.com/manga/{path}.html"
    request_manga = by_pass_data(link, 10)
    localhost = split_join(request.url)
    soup_manga = BeautifulSoup(request_manga, "html.parser")
    manga = soup_manga.find("div", class_="manga")

    manga_title = manga.find("div", class_="ttline").text
    if manga_title:
        manga_title = manga.find("div", class_="ttline").find("h1").text
    else:
        manga_title = ""

    manga_poster = ""
    try:
        manga_poster = manga.find("img").get("src")
    except:
        pass

    description = ""
    try:
        description = (
            manga.find("p", itemprop="description").text.replace("\n", "").strip()
        )
    except:
        pass

    cats = manga.find("li", itemprop="genre")
    try:
        categories = []
        for category in cats.find_all("a"):
            categories.append(category.text)
    except:
        pass

    status = ""
    try:
        status = manga.find("a", href="/category/updated.html").text
    except:
        pass

    author = ""
    try:
        author = manga.find("a", itemprop="author").text
    except:
        pass

    list_chapter = manga.find_all("a", class_="chapter_list_a")
    chapters = {}
    chapters_name = []
    for chapter in list_chapter:
        chapter_title = chapter.text
        chapters_name.append(chapter_title)
        original_link_chapter = chapter.get("href")
        url = original_link_chapter.split("/")
        path_segment_chapter = url[4]
        id_chapter = url[5].replace(".html", "")
        chapter_link_server = make_link(
            localhost, f"/web/rmanga/14/{path_segment_chapter}/{id_chapter}/"
        )
        chapters[f"{chapter_title}"] = chapter_link_server

    str_chapters = ", ".join(chapters_name)
    str_categories = ", ".join(categories)

    manga_info = {
        "genres": "manga",
        "id_manga": id_manga,
        "title": manga_title,
        "description": description,
        "poster": manga_poster,
        "categories": str_categories,
        "status": status,
        "author": author,
        "chapters": chapters,
    }

    try:
        if check_manga(path):
            insertMangaIntoTable(
                id_manga,
                "0",
                "5.0",
                description,
                manga_poster,
                link,
                str_chapters,
                author,
                str_categories,
                status,
                manga_title,
                base_link,
                "",
            )
    except:
        pass

    return manga_info


def get_image_chapter_server_14(path, id_chapter):
    base_link = "https://br.ninemanga.com"
    images = []
    path = urllib.parse.quote(path)
    link_chapter = f"{base_link}/chapter/{path}/{id_chapter}"
    request = by_pass_data(f"{link_chapter}-10-1.html", 10)
    soup_chapter = BeautifulSoup(request, "html.parser")

    # GET ID_MANGA
    tmp = soup_chapter.find("div", class_="subgiude").find_all("li")
    id_manga = base_link + tmp[1].find("a").text
    title_manga = tmp[1].find("a").text

    # Get path_segment manga
    path_segment_manga = urllib.parse.quote_plus(title_manga)

    link_chapter_original = f"{base_link}/chapter/{path_segment_manga}/{id_chapter}/"

    title_chapter = ""
    try:
        title_chapter = (
            soup_chapter.find("div", class_="tip").find_all("a", limit=1)[0].text
        )
    except:
        pass
    selectchapter = soup_chapter.find("div", class_="changepage")

    indexchapterstr = selectchapter.find("option")
    if indexchapterstr is not None:
        indexchapterstrs = indexchapterstr.text
        indexchapters = indexchapterstrs[2:]
        totalAllchapters = int(indexchapters)

    for indexchapter in range(totalAllchapters):
        link_chapter_10 = link_chapter + "-10-" + str(indexchapter + 1) + ".html"
        request_All_link_chapter10 = by_pass_data(link_chapter_10, 4)
        soup_All_linkchapter_10 = BeautifulSoup(
            request_All_link_chapter10, "html.parser"
        )
        for image_All in soup_All_linkchapter_10.find_all("div", class_="pic_box"):
            for image in image_All.findAll("img"):
                x = image.get("src")
                # y = uploadImagetoImgbb(image.get('src'))
                images.append(x)
                # backup.append(y)
    chapter_info = {
        "title": title_manga,
        "image_chapter": images,
        "chapter_title": title_chapter,
    }

    try:
        if check_chapter(link_chapter):
            insertListChapter(
                link_chapter_original,
                title_chapter,
                id_chapter,
                id_manga,
            )
    except:
        pass

    try:
        str_images = ",".join(images)
        if check_image_chapter(path_segment_manga, id_chapter):
            insertImageChapter(
                f"{path_segment_manga}-{id_chapter}",
                f"{base_link}/chapter/{path_segment_manga}/{id_chapter}/",
                "",
                str_images,
            )
    except:
        pass

    return chapter_info


# RU.NINEMANGA
def get_lasted_manga_updates_server_15():
    base_link = "https://ru.ninemanga.com"
    session["server"] = 15
    full_latest_update = []
    link = "https://ru.ninemanga.com/list/New-Update/"

    localhost = split_join(request.url)
    request_home = by_pass_data(link, 10)
    soup_home = BeautifulSoup(request_home, "html.parser")

    for latest_Update in soup_home.find_all("ul", class_="direlist"):
        for manga in latest_Update.find_all("li"):

            manga_link_original = manga.find("a").get("href")
            manga_poster = manga.find("img").get("src")
            manga_title = manga.find("a", class_="bookname").text
            if manga_title == "":
                continue
            description_manga = manga.find("p").text
            chapter_link_original = manga.find("a", class_="chaptername").get("href")
            chapter = manga.find("a", class_="chaptername").text
            path_segment_manga = manga_link_original.split("/")[4]

            url = chapter_link_original.split("/")
            if len(url) == 5:
                continue
            path_segment_chapter = url[4]
            id_chapter = url[5]

            manga_link_server = make_link(
                localhost, f"/web/rmanga/15/{path_segment_manga}/"
            )
            chapter_link_server = make_link(
                localhost, f"/web/rmanga/15/{path_segment_chapter}/{id_chapter}/"
            )

            manga_detail = {
                "id_manga": manga_link_original,
                "title_manga": manga_title.replace("\n", ""),
                "image_poster_link_goc": manga_poster,
                "description_manga": description_manga,
                "path_segment_manga": path_segment_manga.replace(".html", ""),
                "url_manga": manga_link_server.replace(".html", ""),
                "chapter_new": chapter.replace("\n", ""),
                "path_segment_chapter": path_segment_chapter,
                "url_chapter": chapter_link_server.replace(".html", ""),
            }
            full_latest_update.append(manga_detail)
    return full_latest_update


def get_hot_manga_server_15():
    base_link = "https://ru.ninemanga.com"
    session["server"] = 15
    hot_manga = []
    link = "https://ru.ninemanga.com/list/Hot-Book/"

    localhost = split_join(request.url)
    request_home = by_pass_data(link, 10)
    soup_home = BeautifulSoup(request_home, "html.parser")

    list_hot_manga = soup_home.find_all("div", class_="mainbox")[1]
    # print(list_hot_manga)
    for manga in list_hot_manga.find_all("dl", class_="bookinfo"):
        id_manga = ""
        try:
            id_manga = manga.find("dt").find("a").get("href")
        except:
            pass

        manga_poster = ""
        try:
            manga_poster = manga.find("dt").find("a").find("img").get("src")
        except:
            pass

        manga_title = ""
        try:
            manga_title = manga.find("dd").find("a", class_="bookname").text.strip()
        except:
            pass

        description_manga = ""
        try:
            description_manga = manga.find("p").text
        except:
            pass

        id_chapter = ""
        try:
            id_chapter = manga.find("a", class_="chaptername").get("href")
        except:
            pass

        chapter_title = ""
        try:
            chapter_title = manga.find("a", class_="chaptername").text
        except:
            pass

        path_segment_manga = id_manga.split("/")[4]

        url = id_chapter.split("/")
        if len(url) == 5:
            continue
        path_segment_chapter = url[4]
        id_chapter = url[5]

        manga_link_server = make_link(
            localhost, f"/web/rmanga/15/{path_segment_manga}/"
        )
        chapter_link_server = make_link(
            localhost, f"/web/rmanga/15/{path_segment_chapter}/{id_chapter}/"
        )

        manga_detail = {
            "id_manga": id_manga,
            "title_manga": manga_title.replace("\n", ""),
            "image_poster_link_goc": manga_poster,
            "description_manga": description_manga,
            "path_segment_manga": path_segment_manga.replace(".html", ""),
            "url_manga": manga_link_server.replace(".html", ""),
            "chapter_new": chapter_title.replace("\n", ""),
            "path_segment_chapter": path_segment_chapter,
            "url_chapter": chapter_link_server.replace(".html", ""),
        }
        hot_manga.append(manga_detail)
        # print("_______check_____", manga_title)
    return hot_manga


def get_manga_server_15(path):
    base_link = "https://ru.ninemanga.com"
    link = f"https://ru.ninemanga.com/manga/{path}.html?waring=1"
    id_manga = f"https://ru.ninemanga.com/manga/{path}.html"
    request_manga = by_pass_data(link, 10)
    localhost = split_join(request.url)
    soup_manga = BeautifulSoup(request_manga, "html.parser")
    manga = soup_manga.find("div", class_="manga")

    manga_title = manga.find("div", class_="ttline").text
    if manga_title:
        manga_title = manga.find("div", class_="ttline").find("h1").text
    else:
        manga_title = ""

    manga_poster = ""
    try:
        manga_poster = manga.find("img").get("src")
    except:
        pass

    description = ""
    try:
        description = (
            manga.find("p", itemprop="description").text.replace("\n", "").strip()
        )
    except:
        pass

    cats = manga.find("li", itemprop="genre")
    try:
        categories = []
        for category in cats.find_all("a"):
            categories.append(category.text)
    except:
        pass

    status = ""
    try:
        status = manga.find("a", href="/category/updated.html").text
    except:
        pass

    author = ""
    try:
        author = manga.find("a", itemprop="author").text
    except:
        pass

    list_chapter = manga.find_all("a", class_="chapter_list_a")
    chapters = {}
    chapters_name = []
    for chapter in list_chapter:
        chapter_title = chapter.text
        chapters_name.append(chapter_title)
        original_link_chapter = chapter.get("href")
        url = original_link_chapter.split("/")
        path_segment_chapter = url[4]
        id_chapter = url[5].replace(".html", "")
        chapter_link_server = make_link(
            localhost, f"/web/rmanga/15/{path_segment_chapter}/{id_chapter}/"
        )
        chapters[f"{chapter_title}"] = chapter_link_server

    str_chapters = ", ".join(chapters_name)
    str_categories = ", ".join(categories)

    manga_info = {
        "genres": "manga",
        "id_manga": id_manga,
        "title": manga_title,
        "description": description,
        "poster": manga_poster,
        "categories": str_categories,
        "status": status,
        "author": author,
        "chapters": chapters,
    }

    try:
        if check_manga(path):
            insertMangaIntoTable(
                id_manga,
                "0",
                "5.0",
                description,
                manga_poster,
                link,
                str_chapters,
                author,
                str_categories,
                status,
                manga_title,
                base_link,
                "",
            )
    except:
        pass

    return manga_info


def get_image_chapter_server_15(path, id_chapter):
    base_link = "https://ru.ninemanga.com"
    images = []
    path = urllib.parse.quote(path)
    link_chapter = f"{base_link}/chapter/{path}/{id_chapter}"
    request = by_pass_data(f"{link_chapter}-10-1.html", 10)
    soup_chapter = BeautifulSoup(request, "html.parser")

    # GET ID_MANGA
    tmp = soup_chapter.find("div", class_="subgiude").find_all("li")
    id_manga = base_link + tmp[1].find("a").text
    title_manga = tmp[1].find("a").text

    # Get path_segment manga
    path_segment_manga = urllib.parse.quote_plus(title_manga)

    link_chapter_original = f"{base_link}/chapter/{path_segment_manga}/{id_chapter}/"

    title_chapter = ""
    try:
        title_chapter = (
            soup_chapter.find("div", class_="tip").find_all("a", limit=1)[0].text
        )
    except:
        pass
    selectchapter = soup_chapter.find("div", class_="changepage")

    indexchapterstr = selectchapter.find("option")
    if indexchapterstr is not None:
        indexchapterstrs = indexchapterstr.text
        indexchapters = indexchapterstrs[2:]
        totalAllchapters = int(indexchapters)

    for indexchapter in range(totalAllchapters):
        link_chapter_10 = link_chapter + "-10-" + str(indexchapter + 1) + ".html"
        request_All_link_chapter10 = by_pass_data(link_chapter_10, 4)
        soup_All_linkchapter_10 = BeautifulSoup(
            request_All_link_chapter10, "html.parser"
        )
        for image_All in soup_All_linkchapter_10.find_all("div", class_="pic_box"):
            for image in image_All.findAll("img"):
                x = image.get("src")
                # y = uploadImagetoImgbb(image.get('src'))
                images.append(x)
                # backup.append(y)
    chapter_info = {
        "title": title_manga,
        "image_chapter": images,
        "chapter_title": title_chapter,
    }

    try:
        if check_chapter(link_chapter):
            insertListChapter(
                link_chapter_original,
                title_chapter,
                id_chapter,
                id_manga,
            )
    except:
        pass

    try:
        str_images = ",".join(images)
        if check_image_chapter(path_segment_manga, id_chapter):
            insertImageChapter(
                f"{path_segment_manga}-{id_chapter}",
                f"{base_link}/chapter/{path_segment_manga}/{id_chapter}/",
                "",
                str_images,
            )
    except:
        pass

    return chapter_info


# ES.NINEMANGA
def get_lasted_manga_updates_server_16():
    base_link = "https://es.ninemanga.com"
    session["server"] = 16
    full_latest_update = []
    link = "https://es.ninemanga.com/list/New-Update/"

    localhost = split_join(request.url)
    request_home = by_pass_data(link, 10)
    soup_home = BeautifulSoup(request_home, "html.parser")

    for latest_Update in soup_home.find_all("ul", class_="direlist"):
        for manga in latest_Update.find_all("li"):

            manga_link_original = manga.find("a").get("href")
            manga_poster = manga.find("img").get("src")
            manga_title = manga.find("a", class_="bookname").text
            if manga_title == "":
                continue
            description_manga = manga.find("p").text
            chapter_link_original = manga.find("a", class_="chaptername").get("href")
            chapter = manga.find("a", class_="chaptername").text
            path_segment_manga = manga_link_original.split("/")[4]

            url = chapter_link_original.split("/")
            if len(url) == 5:
                continue
            path_segment_chapter = url[4]
            id_chapter = url[5]

            manga_link_server = make_link(
                localhost, f"/web/rmanga/16/{path_segment_manga}/"
            )
            chapter_link_server = make_link(
                localhost, f"/web/rmanga/16/{path_segment_chapter}/{id_chapter}/"
            )

            manga_detail = {
                "id_manga": manga_link_original,
                "title_manga": manga_title.replace("\n", ""),
                "image_poster_link_goc": manga_poster,
                "description_manga": description_manga,
                "path_segment_manga": path_segment_manga.replace(".html", ""),
                "url_manga": manga_link_server.replace(".html", ""),
                "chapter_new": chapter.replace("\n", ""),
                "path_segment_chapter": path_segment_chapter,
                "url_chapter": chapter_link_server.replace(".html", ""),
            }
            full_latest_update.append(manga_detail)
    return full_latest_update


def get_hot_manga_server_16():
    base_link = "https://es.ninemanga.com"
    session["server"] = 16
    hot_manga = []
    link = "https://es.ninemanga.com/list/New-Update/"

    localhost = split_join(request.url)
    request_home = by_pass_data(link, 10)
    soup_home = BeautifulSoup(request_home, "html.parser")

    list_hot_manga = soup_home.find_all("div", class_="mainbox")[1]
    # print(list_hot_manga)
    for manga in list_hot_manga.find_all("dl", class_="bookinfo"):
        id_manga = ""
        try:
            id_manga = manga.find("dt").find("a").get("href")
        except:
            pass

        manga_poster = ""
        try:
            manga_poster = manga.find("dt").find("a").find("img").get("src")
        except:
            pass

        manga_title = ""
        try:
            manga_title = manga.find("dd").find("a", class_="bookname").text.strip()
        except:
            pass

        description_manga = ""
        try:
            description_manga = manga.find("p").text
        except:
            pass

        id_chapter = ""
        try:
            id_chapter = manga.find("a", class_="chaptername").get("href")
        except:
            pass

        chapter_title = ""
        try:
            chapter_title = manga.find("a", class_="chaptername").text
        except:
            pass

        path_segment_manga = id_manga.split("/")[4]

        url = id_chapter.split("/")
        if len(url) == 5:
            continue
        path_segment_chapter = url[4]
        id_chapter = url[5]

        manga_link_server = make_link(
            localhost, f"/web/rmanga/16/{path_segment_manga}/"
        )
        chapter_link_server = make_link(
            localhost, f"/web/rmanga/16/{path_segment_chapter}/{id_chapter}/"
        )

        manga_detail = {
            "id_manga": id_manga,
            "title_manga": manga_title.replace("\n", ""),
            "image_poster_link_goc": manga_poster,
            "description_manga": description_manga,
            "path_segment_manga": path_segment_manga.replace(".html", ""),
            "url_manga": manga_link_server.replace(".html", ""),
            "chapter_new": chapter_title.replace("\n", ""),
            "path_segment_chapter": path_segment_chapter,
            "url_chapter": chapter_link_server.replace(".html", ""),
        }
        hot_manga.append(manga_detail)
        # print("_______check_____", manga_title)
    return hot_manga


def get_manga_server_16(path):
    base_link = "https://es.ninemanga.com"
    link = f"https://es.ninemanga.com/manga/{path}.html?waring=1"
    id_manga = f"https://es.ninemanga.com/manga/{path}.html"
    request_manga = by_pass_data(link, 10)
    localhost = split_join(request.url)
    soup_manga = BeautifulSoup(request_manga, "html.parser")
    manga = soup_manga.find("div", class_="manga")

    manga_title = manga.find("div", class_="ttline").text
    if manga_title:
        manga_title = manga.find("div", class_="ttline").find("h1").text
    else:
        manga_title = ""

    manga_poster = ""
    try:
        manga_poster = manga.find("img").get("src")
    except:
        pass

    description = ""
    try:
        description = (
            manga.find("p", itemprop="description").text.replace("\n", "").strip()
        )
    except:
        pass

    cats = manga.find("li", itemprop="genre")
    try:
        categories = []
        for category in cats.find_all("a"):
            categories.append(category.text)
    except:
        pass

    status = ""
    try:
        status = manga.find("a", href="/category/updated.html").text
    except:
        pass

    author = ""
    try:
        author = manga.find("a", itemprop="author").text
    except:
        pass

    list_chapter = manga.find_all("a", class_="chapter_list_a")
    chapters = {}
    chapters_name = []
    for chapter in list_chapter:
        chapter_title = chapter.text
        chapters_name.append(chapter_title)
        original_link_chapter = chapter.get("href")
        url = original_link_chapter.split("/")
        path_segment_chapter = url[4]
        id_chapter = url[5].replace(".html", "")
        chapter_link_server = make_link(
            localhost, f"/web/rmanga/16/{path_segment_chapter}/{id_chapter}/"
        )
        chapters[f"{chapter_title}"] = chapter_link_server

    str_chapters = ", ".join(chapters_name)
    str_categories = ", ".join(categories)

    manga_info = {
        "genres": "manga",
        "id_manga": id_manga,
        "title": manga_title,
        "description": description,
        "poster": manga_poster,
        "categories": str_categories,
        "status": status,
        "author": author,
        "chapters": chapters,
    }

    try:
        if check_manga(path):
            insertMangaIntoTable(
                id_manga,
                "0",
                "5.0",
                description,
                manga_poster,
                link,
                str_chapters,
                author,
                str_categories,
                status,
                manga_title,
                base_link,
                "",
            )
    except:
        pass

    return manga_info


def get_image_chapter_server_16(path, id_chapter):
    base_link = "https://es.ninemanga.com"
    images = []
    path = urllib.parse.quote(path)
    link_chapter = f"{base_link}/chapter/{path}/{id_chapter}"
    request = by_pass_data(f"{link_chapter}-10-1.html", 10)
    soup_chapter = BeautifulSoup(request, "html.parser")

    # GET ID_MANGA
    tmp = soup_chapter.find("div", class_="subgiude").find_all("li")
    id_manga = base_link + tmp[1].find("a").text
    title_manga = tmp[1].find("a").text

    # Get path_segment manga
    path_segment_manga = urllib.parse.quote_plus(title_manga)

    link_chapter_original = f"{base_link}/chapter/{path_segment_manga}/{id_chapter}/"

    title_chapter = ""
    try:
        title_chapter = (
            soup_chapter.find("div", class_="tip").find_all("a", limit=1)[0].text
        )
    except:
        pass
    selectchapter = soup_chapter.find("div", class_="changepage")

    indexchapterstr = selectchapter.find("option")
    if indexchapterstr is not None:
        indexchapterstrs = indexchapterstr.text
        indexchapters = indexchapterstrs[2:]
        totalAllchapters = int(indexchapters)
        # print(totalAllchapters)
    for indexchapter in range(totalAllchapters):
        link_chapter_10 = link_chapter + "-10-" + str(indexchapter + 1) + ".html"
        request_All_link_chapter10 = by_pass_data(link_chapter_10, 5)
        soup_All_linkchapter_10 = BeautifulSoup(
            request_All_link_chapter10, "html.parser"
        )
        for image_All in soup_All_linkchapter_10.find_all("div", class_="pic_box"):
            for image in image_All.findAll("img"):
                x = image.get("src")
                # y = uploadImagetoImgbb(image.get('src'))
                images.append(x)
                # print(x)
                # backup.append(y)
    chapter_info = {
        "title": title_manga,
        "image_chapter": images,
        "chapter_title": title_chapter,
    }

    try:
        if check_chapter(link_chapter):
            insertListChapter(
                link_chapter_original,
                title_chapter,
                id_chapter,
                id_manga,
            )
    except:
        pass

    try:
        str_images = ",".join(images)
        if check_image_chapter(path_segment_manga, id_chapter):
            insertImageChapter(
                f"{path_segment_manga}-{id_chapter}",
                f"{base_link}/chapter/{path_segment_manga}/{id_chapter}/",
                "",
                str_images,
            )
    except:
        pass

    return chapter_info


# FR.NINEMANGA
def get_lasted_manga_updates_server_17():
    base_link = "https://fr.ninemanga.com"
    session["server"] = 17
    full_latest_update = []
    link = "https://fr.ninemanga.com/list/New-Update/"

    localhost = split_join(request.url)
    request_home = by_pass_data(link, 10)
    soup_home = BeautifulSoup(request_home, "html.parser")

    for latest_Update in soup_home.find_all("ul", class_="direlist"):
        for manga in latest_Update.find_all("li"):

            manga_link_original = manga.find("a").get("href")
            manga_poster = manga.find("img").get("src")
            manga_title = manga.find("a", class_="bookname").text
            if manga_title == "":
                continue
            description_manga = manga.find("p").text
            chapter_link_original = manga.find("a", class_="chaptername").get("href")
            chapter = manga.find("a", class_="chaptername").text
            path_segment_manga = manga_link_original.split("/")[4]

            url = chapter_link_original.split("/")
            if len(url) == 5:
                continue
            path_segment_chapter = url[4]
            id_chapter = url[5]

            manga_link_server = make_link(
                localhost, f"/web/rmanga/17/{path_segment_manga}/"
            )
            chapter_link_server = make_link(
                localhost, f"/web/rmanga/17/{path_segment_chapter}/{id_chapter}/"
            )

            manga_detail = {
                "id_manga": manga_link_original,
                "title_manga": manga_title.replace("\n", ""),
                "image_poster_link_goc": manga_poster,
                "description_manga": description_manga,
                "path_segment_manga": path_segment_manga.replace(".html", ""),
                "url_manga": manga_link_server.replace(".html", ""),
                "chapter_new": chapter.replace("\n", ""),
                "path_segment_chapter": path_segment_chapter,
                "url_chapter": chapter_link_server.replace(".html", ""),
            }
            full_latest_update.append(manga_detail)
    return full_latest_update


def get_hot_manga_server_17():
    base_link = "https://fr.ninemanga.com"
    session["server"] = 17
    hot_manga = []
    link = "https://fr.ninemanga.com/list/Hot-Book/"

    localhost = split_join(request.url)
    request_home = by_pass_data(link, 10)
    soup_home = BeautifulSoup(request_home, "html.parser")

    list_hot_manga = soup_home.find_all("div", class_="mainbox")[1]
    # print(list_hot_manga)
    for manga in list_hot_manga.find_all("dl", class_="bookinfo"):
        id_manga = ""
        try:
            id_manga = manga.find("dt").find("a").get("href")
        except:
            pass

        manga_poster = ""
        try:
            manga_poster = manga.find("dt").find("a").find("img").get("src")
        except:
            pass

        manga_title = ""
        try:
            manga_title = manga.find("dd").find("a", class_="bookname").text.strip()
        except:
            pass

        description_manga = ""
        try:
            description_manga = manga.find("p").text
        except:
            pass

        id_chapter = ""
        try:
            id_chapter = manga.find("a", class_="chaptername").get("href")
        except:
            pass

        chapter_title = ""
        try:
            chapter_title = manga.find("a", class_="chaptername").text
        except:
            pass

        path_segment_manga = id_manga.split("/")[4]

        url = id_chapter.split("/")
        if len(url) == 5:
            continue
        path_segment_chapter = url[4]
        id_chapter = url[5]

        manga_link_server = make_link(
            localhost, f"/web/rmanga/17/{path_segment_manga}/"
        )
        chapter_link_server = make_link(
            localhost, f"/web/rmanga/17/{path_segment_chapter}/{id_chapter}/"
        )

        manga_detail = {
            "id_manga": id_manga,
            "title_manga": manga_title.replace("\n", ""),
            "image_poster_link_goc": manga_poster,
            "description_manga": description_manga,
            "path_segment_manga": path_segment_manga.replace(".html", ""),
            "url_manga": manga_link_server.replace(".html", ""),
            "chapter_new": chapter_title.replace("\n", ""),
            "path_segment_chapter": path_segment_chapter,
            "url_chapter": chapter_link_server.replace(".html", ""),
        }
        hot_manga.append(manga_detail)
        # print("_______check_____", manga_title)
    return hot_manga


def get_manga_server_17(path):
    base_link = "https://fr.ninemanga.com"
    link = f"https://fr.ninemanga.com/manga/{path}.html?waring=1"
    id_manga = f"https://fr.ninemanga.com/manga/{path}.html"
    request_manga = by_pass_data(link, 10)
    localhost = split_join(request.url)
    soup_manga = BeautifulSoup(request_manga, "html.parser")
    manga = soup_manga.find("div", class_="manga")

    manga_title = manga.find("div", class_="ttline").text
    if manga_title:
        manga_title = manga.find("div", class_="ttline").find("h1").text
    else:
        manga_title = ""

    manga_poster = ""
    try:
        manga_poster = manga.find("img").get("src")
    except:
        pass

    description = ""
    try:
        description = (
            manga.find("p", itemprop="description").text.replace("\n", "").strip()
        )
    except:
        pass

    cats = manga.find("li", itemprop="genre")
    try:
        categories = []
        for category in cats.find_all("a"):
            categories.append(category.text)
    except:
        pass

    status = ""
    try:
        status = manga.find("a", href="/category/updated.html").text
    except:
        pass

    author = ""
    try:
        author = manga.find("a", itemprop="author").text
    except:
        pass

    list_chapter = manga.find_all("a", class_="chapter_list_a")
    chapters = {}
    chapters_name = []
    for chapter in list_chapter:
        chapter_title = chapter.text
        chapters_name.append(chapter_title)
        original_link_chapter = chapter.get("href")
        url = original_link_chapter.split("/")
        path_segment_chapter = url[4]
        id_chapter = url[5].replace(".html", "")
        chapter_link_server = make_link(
            localhost, f"/web/rmanga/17/{path_segment_chapter}/{id_chapter}/"
        )
        chapters[f"{chapter_title}"] = chapter_link_server

    str_chapters = ", ".join(chapters_name)
    str_categories = ", ".join(categories)

    manga_info = {
        "genres": "manga",
        "id_manga": id_manga,
        "title": manga_title,
        "description": description,
        "poster": manga_poster,
        "categories": str_categories,
        "status": status,
        "author": author,
        "chapters": chapters,
    }

    try:
        if check_manga(path):
            insertMangaIntoTable(
                id_manga,
                "0",
                "5.0",
                description,
                manga_poster,
                link,
                str_chapters,
                author,
                str_categories,
                status,
                manga_title,
                base_link,
                "",
            )
    except:
        pass

    return manga_info


def get_image_chapter_server_17(path, id_chapter):
    base_link = "https://fr.ninemanga.com"
    images = []
    path = urllib.parse.quote(path)
    link_chapter = f"{base_link}/chapter/{path}/{id_chapter}"
    request = by_pass_data(f"{link_chapter}-10-1.html", 10)
    soup_chapter = BeautifulSoup(request, "html.parser")

    # GET ID_MANGA
    tmp = soup_chapter.find("div", class_="subgiude").find_all("li")
    id_manga = base_link + tmp[1].find("a").text
    title_manga = tmp[1].find("a").text

    # Get path_segment manga
    path_segment_manga = urllib.parse.quote_plus(title_manga)

    link_chapter_original = f"{base_link}/chapter/{path_segment_manga}/{id_chapter}/"

    title_chapter = ""
    try:
        title_chapter = (
            soup_chapter.find("div", class_="tip").find_all("a", limit=1)[0].text
        )
    except:
        pass
    selectchapter = soup_chapter.find("div", class_="changepage")

    indexchapterstr = selectchapter.find("option")
    if indexchapterstr is not None:
        indexchapterstrs = indexchapterstr.text
        indexchapters = indexchapterstrs[2:]
        totalAllchapters = int(indexchapters)

    for indexchapter in range(totalAllchapters):
        link_chapter_10 = link_chapter + "-10-" + str(indexchapter + 1) + ".html"
        request_All_link_chapter10 = by_pass_data(link_chapter_10, 5)
        soup_All_linkchapter_10 = BeautifulSoup(
            request_All_link_chapter10, "html.parser"
        )
        for image_All in soup_All_linkchapter_10.find_all("div", class_="pic_box"):
            for image in image_All.findAll("img"):
                x = image.get("src")
                # y = uploadImagetoImgbb(image.get('src'))
                images.append(x)
                # backup.append(y)
    chapter_info = {
        "title": title_manga,
        "image_chapter": images,
        "chapter_title": title_chapter,
    }

    try:
        if check_chapter(link_chapter):
            insertListChapter(
                link_chapter_original,
                title_chapter,
                id_chapter,
                id_manga,
            )
    except:
        pass

    try:
        str_images = ",".join(images)
        if check_image_chapter(path_segment_manga, id_chapter):
            insertImageChapter(
                f"{path_segment_manga}-{id_chapter}",
                f"{base_link}/chapter/{path_segment_manga}/{id_chapter}/",
                "",
                str_images,
            )
    except:
        pass

    return chapter_info


# IT.NINEMANGA
def get_lasted_manga_updates_server_18():
    base_link = "https://it.ninemanga.com"
    session["server"] = 18
    full_latest_update = []
    link = "https://it.ninemanga.com/list/New-Update/"

    localhost = split_join(request.url)
    request_home = by_pass_data(link, 10)
    soup_home = BeautifulSoup(request_home, "html.parser")

    for latest_Update in soup_home.find_all("ul", class_="direlist"):
        for manga in latest_Update.find_all("li"):

            manga_link_original = manga.find("a").get("href")
            manga_poster = manga.find("img").get("src")
            manga_title = manga.find("a", class_="bookname").text
            if manga_title == "":
                continue
            description_manga = manga.find("p").text
            chapter_link_original = manga.find("a", class_="chaptername").get("href")
            chapter = manga.find("a", class_="chaptername").text
            path_segment_manga = manga_link_original.split("/")[4]

            url = chapter_link_original.split("/")
            if len(url) == 5:
                continue
            path_segment_chapter = url[4]
            id_chapter = url[5]

            manga_link_server = make_link(
                localhost, f"/web/rmanga/18/{path_segment_manga}/"
            )
            chapter_link_server = make_link(
                localhost, f"/web/rmanga/18/{path_segment_chapter}/{id_chapter}/"
            )

            manga_detail = {
                "id_manga": manga_link_original,
                "title_manga": manga_title.replace("\n", ""),
                "image_poster_link_goc": manga_poster,
                "description_manga": description_manga,
                "path_segment_manga": path_segment_manga.replace(".html", ""),
                "url_manga": manga_link_server.replace(".html", ""),
                "chapter_new": chapter.replace("\n", ""),
                "path_segment_chapter": path_segment_chapter,
                "url_chapter": chapter_link_server.replace(".html", ""),
            }
            full_latest_update.append(manga_detail)
    return full_latest_update


def get_hot_manga_server_18():
    base_link = "https://it.ninemanga.com"
    session["server"] = 18
    hot_manga = []
    link = "https://it.ninemanga.com/list/Hot-Book/"

    localhost = split_join(request.url)
    request_home = by_pass_data(link, 10)
    soup_home = BeautifulSoup(request_home, "html.parser")

    list_hot_manga = soup_home.find_all("div", class_="mainbox")[1]
    # print(list_hot_manga)
    for manga in list_hot_manga.find_all("dl", class_="bookinfo"):
        id_manga = ""
        try:
            id_manga = manga.find("dt").find("a").get("href")
        except:
            pass

        manga_poster = ""
        try:
            manga_poster = manga.find("dt").find("a").find("img").get("src")
        except:
            pass

        manga_title = ""
        try:
            manga_title = manga.find("dd").find("a", class_="bookname").text.strip()
        except:
            pass

        description_manga = ""
        try:
            description_manga = manga.find("p").text
        except:
            pass

        id_chapter = ""
        try:
            id_chapter = manga.find("a", class_="chaptername").get("href")
        except:
            pass

        chapter_title = ""
        try:
            chapter_title = manga.find("a", class_="chaptername").text
        except:
            pass

        path_segment_manga = id_manga.split("/")[4]

        url = id_chapter.split("/")
        if len(url) == 5:
            continue
        path_segment_chapter = url[4]
        id_chapter = url[5]

        manga_link_server = make_link(
            localhost, f"/web/rmanga/18/{path_segment_manga}/"
        )
        chapter_link_server = make_link(
            localhost, f"/web/rmanga/18/{path_segment_chapter}/{id_chapter}/"
        )

        manga_detail = {
            "id_manga": id_manga,
            "title_manga": manga_title.replace("\n", ""),
            "image_poster_link_goc": manga_poster,
            "description_manga": description_manga,
            "path_segment_manga": path_segment_manga.replace(".html", ""),
            "url_manga": manga_link_server.replace(".html", ""),
            "chapter_new": chapter_title.replace("\n", ""),
            "path_segment_chapter": path_segment_chapter,
            "url_chapter": chapter_link_server.replace(".html", ""),
        }
        hot_manga.append(manga_detail)
        # print("_______check_____", manga_title)
    return hot_manga


def get_manga_server_18(path):
    base_link = "https://it.ninemanga.com"
    link = f"https://it.ninemanga.com/manga/{path}.html?waring=1"
    id_manga = f"https://it.ninemanga.com/manga/{path}.html"
    request_manga = by_pass_data(link, 10)
    localhost = split_join(request.url)
    soup_manga = BeautifulSoup(request_manga, "html.parser")
    manga = soup_manga.find("div", class_="manga")

    manga_title = manga.find("div", class_="ttline").text
    if manga_title:
        manga_title = manga.find("div", class_="ttline").find("h1").text
    else:
        manga_title = ""

    manga_poster = ""
    try:
        manga_poster = manga.find("img").get("src")
    except:
        pass

    description = ""
    try:
        description = (
            manga.find("p", itemprop="description").text.replace("\n", "").strip()
        )
    except:
        pass

    cats = manga.find("li", itemprop="genre")
    try:
        categories = []
        for category in cats.find_all("a"):
            categories.append(category.text)
    except:
        pass

    status = ""
    try:
        status = manga.find("a", href="/category/updated.html").text
    except:
        pass

    author = ""
    try:
        author = manga.find("a", itemprop="author").text
    except:
        pass

    list_chapter = manga.find_all("a", class_="chapter_list_a")
    chapters = {}
    chapters_name = []
    for chapter in list_chapter:
        chapter_title = chapter.text
        chapters_name.append(chapter_title)
        original_link_chapter = chapter.get("href")
        url = original_link_chapter.split("/")
        path_segment_chapter = url[4]
        id_chapter = url[5].replace(".html", "")
        chapter_link_server = make_link(
            localhost, f"/web/rmanga/18/{path_segment_chapter}/{id_chapter}/"
        )
        chapters[f"{chapter_title}"] = chapter_link_server

    str_chapters = ", ".join(chapters_name)
    str_categories = ", ".join(categories)

    manga_info = {
        "genres": "manga",
        "id_manga": id_manga,
        "title": manga_title,
        "description": description,
        "poster": manga_poster,
        "categories": str_categories,
        "status": status,
        "author": author,
        "chapters": chapters,
    }

    try:
        if check_manga(path):
            insertMangaIntoTable(
                id_manga,
                "0",
                "5.0",
                description,
                manga_poster,
                link,
                str_chapters,
                author,
                str_categories,
                status,
                manga_title,
                base_link,
                "",
            )
    except:
        pass

    return manga_info


def get_image_chapter_server_18(path, id_chapter):
    base_link = "https://it.ninemanga.com"
    images = []
    path = urllib.parse.quote(path)
    link_chapter = f"{base_link}/chapter/{path}/{id_chapter}"
    request = by_pass_data(f"{link_chapter}-10-1.html", 10)
    soup_chapter = BeautifulSoup(request, "html.parser")

    # GET ID_MANGA
    tmp = soup_chapter.find("div", class_="subgiude").find_all("li")
    id_manga = base_link + tmp[1].find("a").text
    title_manga = tmp[1].find("a").text

    # Get path_segment manga
    path_segment_manga = urllib.parse.quote_plus(title_manga)

    link_chapter_original = f"{base_link}/chapter/{path_segment_manga}/{id_chapter}/"

    title_chapter = ""
    try:
        title_chapter = (
            soup_chapter.find("div", class_="tip").find_all("a", limit=1)[0].text
        )
    except:
        pass
    selectchapter = soup_chapter.find("div", class_="changepage")

    indexchapterstr = selectchapter.find("option")
    if indexchapterstr is not None:
        indexchapterstrs = indexchapterstr.text
        indexchapters = indexchapterstrs[2:]
        totalAllchapters = int(indexchapters)

    for indexchapter in range(totalAllchapters):
        link_chapter_10 = link_chapter + "-10-" + str(indexchapter + 1) + ".html"
        request_All_link_chapter10 = by_pass_data(link_chapter_10, 5)
        soup_All_linkchapter_10 = BeautifulSoup(
            request_All_link_chapter10, "html.parser"
        )
        for image_All in soup_All_linkchapter_10.find_all("div", class_="pic_box"):
            for image in image_All.findAll("img"):
                x = image.get("src")
                # y = uploadImagetoImgbb(image.get('src'))
                # print("______check___link:  ", str(x))
                images.append(x)
                # backup.append(y)
    chapter_info = {
        "title": title_manga,
        "image_chapter": images,
        "chapter_title": title_chapter,
    }

    try:
        if check_chapter(link_chapter):
            insertListChapter(
                link_chapter_original,
                title_chapter,
                id_chapter,
                id_manga,
            )
    except:
        pass

    try:
        str_images = ",".join(images)
        if check_image_chapter(path_segment_manga, id_chapter):
            insertImageChapter(
                f"{path_segment_manga}-{id_chapter}",
                f"{base_link}/chapter/{path_segment_manga}/{id_chapter}/",
                "",
                str_images,
            )
    except:
        pass

    return chapter_info


# AZORA
def get_lasted_manga_updates_server_19():
    base_link = "https://azoramoon.com"
    session["server"] = 19
    full_latest_update = []
    localhost = split_join(request.url)
    link_lastest_update = "https://azoramoon.com/"
    request_home = requests.get(link_lastest_update)
    soup_home = BeautifulSoup(request_home.text, "html.parser")

    lastest_update = soup_home.find("div", class_="c-page-content style-1")
    for manga in lastest_update.find_all("div", class_="page-item-detail manga"):
        id_manga = (
            manga.find("div", class_="item-thumb c-image-hover").find("a").get("href")
        )
        manga_title = (
            manga.find("div", class_="item-summary")
            .find("div", class_="post-title font-title")
            .find("a")
            .text
        )
        path_segment_manga = id_manga.split("/")[-2]

        chapter_new = manga.find("div", class_="list-chapter").find_all("a", limit=1)
        id_chapter = chapter_new[0].get("href")
        chapter_title = chapter_new[0].text.strip()
        path_segment_chapter = id_chapter.split("/")[-2]

        manga_poster = manga.find("img").get("src")

        manga_link_server = make_link(
            localhost, f"/web/rmanga/19/{path_segment_manga}/"
        )
        chapter_link_server = make_link(
            localhost, f"/web/rmanga/19/{path_segment_manga}/{path_segment_chapter}/"
        )

        manga_detail = {
            "id_manga": id_manga,
            "title_manga": manga_title,
            "image_poster_link_goc": manga_poster,
            "description_manga": "",
            "path_segment_manga": path_segment_manga,
            "url_manga": manga_link_server,
            "chapter_new": chapter_title,
            "path_segment_chapter": path_segment_chapter,
            "url_chapter": chapter_link_server,
        }
        full_latest_update.append(manga_detail)

    return full_latest_update


def get_popular_manga_server_19():
    base_link = "https://azoramoon.com"
    session["server"] = 19
    full_popular_manga = []
    localhost = split_join(request.url)
    request_home = requests.get(base_link)
    soup_home = BeautifulSoup(request_home.text, "html.parser")

    popular_mangas = soup_home.find("div", class_="sidebar-col col-md-4 col-sm-4")
    for manga in popular_mangas.find_all("div", class_="popular-item-wrap"):
        id_manga = ""
        try:
            id_manga = (
                manga.find("div", class_="popular-img widget-thumbnail c-image-hover")
                .find("a")
                .get("href")
            )
        except:
            pass

        title_manga = ""
        try:
            title_manga = (
                manga.find("div", class_="popular-img widget-thumbnail c-image-hover")
                .find("a")
                .get("title")
            )
        except:
            pass

        poster_manga = ""
        try:
            poster_manga = (
                manga.find("div", class_="popular-img widget-thumbnail c-image-hover")
                .find("a")
                .find("img")
                .get("src")
            )
        except:
            pass

        info_chapter = manga.find("div", class_="list-chapter").find_all(
            "span", class_="chapter font-meta"
        )[0]

        id_chapter = ""
        try:
            id_chapter = info_chapter.find("a", class_="btn-link").get("href")
        except:
            pass

        title_chapter = ""
        try:
            title_chapter = info_chapter.find("a", class_="btn-link").text
        except:
            pass

        path_segment_manga = id_manga.split("/")[-2]
        path_segment_chapter = id_chapter.split("/")[-2]

        manga_link_server = make_link(
            localhost, f"/web/rmanga/19/{path_segment_manga}/"
        )
        chapter_link_server = make_link(
            localhost, f"/web/rmanga/19/{path_segment_manga}/{path_segment_chapter}/"
        )

        manga_detail = {
            "id_manga": id_manga,
            "title_manga": title_manga,
            "image_poster_link_goc": poster_manga,
            "description_manga": "",
            "path_segment_manga": path_segment_manga,
            "url_manga": manga_link_server,
            "chapter_new": title_chapter,
            "path_segment_chapter": path_segment_chapter,
            "url_chapter": chapter_link_server,
        }

        full_popular_manga.append(manga_detail)

    return full_popular_manga


def get_manga_server_19(path):
    base_link = "https://azoramoon.com"
    link = f"https://azoramoon.com/series/{path}/"
    request_manga = requests.get(link)
    localhost = split_join(request.url)
    soup_manga = BeautifulSoup(request_manga.text, "html.parser")
    manga = soup_manga
    manga_info = manga.find("div", class_="manga-summary")

    manga_title = ""
    try:
        manga_title = (
            manga.find_all("div", class_="site-content")[0]
            .find("div", class_="post-title")
            .find("h1")
            .text.strip()
        )
    except:
        pass

    manga_poster = ""
    try:
        manga_poster = manga.find("div", class_="summary_image").find("img").get("src")
    except:
        pass

    description = ""
    try:
        description = manga_info.find("p").text.strip()
    except:
        pass

    categories = []
    try:
        cats = manga.find_all("div", class_="summary-content")[0].find(
            "div", class_="genres-content"
        )
        for category in cats.find_all("a"):
            categories.append(category.text)
    except:
        pass

    status = ""
    try:
        status = (
            manga.find_all("div", class_="summary-content")[1].find("div").text.strip()
        )
    except:
        pass

    author = ""

    list_chapter = manga.find("ul", class_="main version-chap no-volumn").find_all("li")
    chapters = {}
    chapters_name = []
    for chapter in list_chapter:
        chapter_info = chapter.find_all("a")[0]
        chapter_title = chapter_info.text.strip()
        chapters_name.append(chapter_title)
        link_chapter = chapter_info.get("href")
        path_segment_chapter = link_chapter.split("/")[-2]
        chapter_link_server = make_link(
            localhost, f"/web/rmanga/19/{path}/{path_segment_chapter}/"
        )
        chapters[f"{chapter_title}"] = chapter_link_server

    str_chapters = ", ".join(chapters_name)
    str_categories = ", ".join(categories)

    manga_info = {
        "genres": "manga",
        "id_manga": link,
        "title": manga_title,
        "description": description,
        "poster": manga_poster,
        "categories": str_categories,
        "status": status,
        "author": author,
        "chapters": chapters,
    }

    try:
        if check_manga(path):
            insertMangaIntoTable(
                link,
                "0",
                "5.0",
                description,
                manga_poster,
                link,
                str_chapters,
                author,
                str_categories,
                status,
                manga_title,
                base_link,
                "",
            )
    except:
        pass

    return manga_info


def get_image_chapter_server_19(path, id_chapter):
    base_link = "https://azoramoon.com"
    images = []
    link_chapter = f"{base_link}/series/{path}/{id_chapter}/"
    request = requests.get(link_chapter)
    soup_chapter = BeautifulSoup(request.text, "html.parser")

    chapter = soup_chapter.find("div", class_="content-area")

    id_manga = ""
    try:
        id_manga = chapter.find("ol", class_="breadcrumb").find_all("a")[1].get("href")
    except:
        pass

    title_manga = ""
    try:
        title_manga = (
            chapter.find("ol", class_="breadcrumb")
            .find_all("a")[1]
            .text.replace("\n", "")
            .strip()
        )
    except:
        pass

    title_chapter = ""
    try:
        title_chapter = (
            chapter.find("ol", class_="breadcrumb")
            .find_all("li")[2]
            .text.replace("\n", "")
            .strip()
        )
    except:
        pass

    list_image = ""
    try:
        data = chapter.find(
            "script", {"type": "text/javascript", "id": "chapter-protector-data"}
        )
        pattern = r'"ct":"(.*?)"'
        list_image = re.search(pattern, data.text).group(1)
        images.append(list_image)
    except:
        pass

    chapter_info = {
        "title": title_manga,
        "image_chapter": images,
        "chapter_title": title_chapter,
    }

    try:
        if check_chapter(link_chapter):
            insertListChapter(
                link_chapter,
                title_chapter,
                id_chapter,
                id_manga,
            )
    except:
        pass

    try:
        str_images = ",".join(images)
        if check_image_chapter(path, id_chapter):
            insertImageChapter(f"{path}-{id_chapter}", link_chapter, "", str_images)
    except:
        pass

    return chapter_info


# def get_lasted_novel_updates_server_11():
#     BASE_LINK = 'https://www.novelhall.com'
#     session["server"] = 11
#     full_latest_update = []
#     localhost = split_join(request.url)
#     request_home = requests.get(BASE_LINK)
#     soup_home = BeautifulSoup(request_home.text, "html.parser")
#     print(soup_home)
#     lastest_update = soup_home.find('div', class_='container').find('div', class_="section3 inner mt30")
#     print(lastest_update)
#     for novel in lastest_update.find_all('tr'):

#         catergories = ''
#         try:
#             catergories = novel.find('td', class_="hidden-xs type").find('a').text.strip()
#         except:
#             pass

#         title_novel = ''
#         id_novel = ''
#         try:
#             title_novel = novel.find('td', class_="w70").find('a').text.strip()
#             id_novel = BASE_LINK + novel.find('td', class_="w70").find('a').get('href')
#         except:
#             pass

#         title_chapter = ''
#         id_chapter = ''
#         try:
#             title_chapter = novel.find('td',class_="hidden-xs").find('a', class_="chapter").text.strip()
#             id_chapter = BASE_LINK + novel.find('td',class_="hidden-xs").find('a', class_="chapter").get('href')
#         except:
#             pass

#         time_update = ''
#         try:
#             time_update = novel.find('td', class_="w30").find('span', class_="time").text
#         except:
#             pass

#         path_segment_novel = id_novel.split('/')[-2]
#         path_segment_chapter = id_chapter.split('/')[-1].replace('.html')

#         link_server_novel = make_link(localhost, f"/web/rnovel/11/{path_segment_novel}/")
#         link_server_chapter = make_link(localhost, f"/web/rnovel/11/{path_segment_novel}/{path_segment_chapter}/")

#         novel_detail = {
#             "id_novel": id_novel,
#             "title_novel": title_novel,
#             "catergories": catergories,
#             "link_server_novel": link_server_novel,
#             "id_chapter": id_chapter,
#             "title_chapter": title_chapter,
#             "link_server_chapter": link_server_chapter,
#             "time_update": time_update
#         }
#         full_latest_update.append(novel_detail)

#     return full_latest_update


def get_lasted_novel_updates_server_4():
    BASE_LINK = "https://bestlightnovel.com/"
    session["server"] = 11
    full_latest_update = []
    localhost = split_join(request.url)
    request_home = requests.get(BASE_LINK)
    soup_home = BeautifulSoup(request_home.text, "html.parser")

    lastest_update = soup_home.find("div", id="contentstory")
    for novel in lastest_update.find_all("div", class_="itemupdate first"):

        poster_novel = ""
        try:
            poster_novel = (
                novel.find("a", class_="tooltip cover").find("img").get("src")
            )
        except:
            pass

        novel_info = novel.find_all("li")
        title_novel = ""
        id_novel = ""
        try:
            title_novel = novel_info[0].find("a", class_="tooltip").text.strip()
            id_novel = novel_info[0].find("a", class_="tooltip").get("href")
        except:
            pass

        title_chapter = ""
        id_chapter = ""
        try:
            title_chapter = novel_info[1].find("a", class_="sts sts_1").text.strip()
            id_chapter = novel_info[1].find("a", class_="sts sts_1").get("href")
        except:
            pass

        time_update = ""
        try:
            time_update = novel_info[1].find("i").text
        except:
            pass

        path_segment_novel = id_novel.split("/")[-1]
        path_segment_chapter = id_chapter.split("/")[-1]

        link_server_novel = make_link(localhost, f"/web/rnovel/4/{path_segment_novel}/")
        link_server_chapter = make_link(
            localhost, f"/web/rnovel/4/{path_segment_novel}/{path_segment_chapter}/"
        )

        novel_detail = {
            "id_novel": id_novel,
            "title_novel": title_novel,
            "poster_novel": poster_novel,
            "link_server_novel": link_server_novel,
            "id_chapter": id_chapter,
            "title_chapter": title_chapter,
            "link_server_chapter": link_server_chapter,
            "time_update": time_update,
        }
        full_latest_update.append(novel_detail)

    return full_latest_update


def get_lasted_novel_updates_server_4():
    BASE_LINK = "https://bestlightnovel.com/"
    session["server"] = 4
    full_latest_update = []
    localhost = split_join(request.url)
    request_home = requests.get(BASE_LINK)
    soup_home = BeautifulSoup(request_home.text, "html.parser")

    lastest_update = soup_home.find("div", id="contentstory")
    for novel in lastest_update.find_all("div", class_="itemupdate first"):

        poster_novel = ""
        try:
            poster_novel = (
                novel.find("a", class_="tooltip cover").find("img").get("src")
            )
        except:
            pass

        novel_info = novel.find_all("li")
        title_novel = ""
        id_novel = ""
        try:
            title_novel = novel_info[0].find("a", class_="tooltip").text.strip()
            id_novel = novel_info[0].find("a", class_="tooltip").get("href")
        except:
            pass

        title_chapter = ""
        id_chapter = ""
        try:
            title_chapter = novel_info[1].find("a", class_="sts sts_1").text.strip()
            id_chapter = novel_info[1].find("a", class_="sts sts_1").get("href")
        except:
            pass

        time_update = ""
        try:
            time_update = novel_info[1].find("i").text
        except:
            pass

        path_segment_novel = id_novel.split("/")[-1]
        path_segment_chapter = id_chapter.split("/")[-1]

        link_server_novel = make_link(localhost, f"/web/rnovel/4/{path_segment_novel}/")
        link_server_chapter = make_link(
            localhost, f"/web/rnovel/4/{path_segment_novel}/{path_segment_chapter}/"
        )

        novel_detail = {
            "id_novel": id_novel,
            "title_novel": title_novel,
            "poster_novel": poster_novel,
            "link_server_novel": link_server_novel,
            "id_chapter": id_chapter,
            "title_chapter": title_chapter,
            "link_server_chapter": link_server_chapter,
            "time_update": time_update,
        }
        full_latest_update.append(novel_detail)

    return full_latest_update


def get_popular_novel_server_4():
    BASE_LINK = "https://bestlightnovel.com/"
    session["server"] = 4
    popular_novel = []
    localhost = split_join(request.url)
    request_home = requests.get(BASE_LINK)
    soup_home = BeautifulSoup(request_home.text, "html.parser")

    list_popular_novel = soup_home.find("div", id="owl-demo")
    for novel in list_popular_novel.find_all("div", class_="item"):

        poster_novel = ""
        try:
            poster_novel = novel.find("img").get("src")

        except:
            pass

        novel_info = novel.find("div", class_="slide-caption")
        title_novel = ""
        id_novel = ""
        try:
            title_novel = novel_info.find("h3").find("a").text.strip()
            id_novel = novel_info.find("h3").find("a").get("href")
        except:
            pass

        title_chapter = ""
        id_chapter = ""
        try:
            title_chapter = novel_info.find("a").text.strip()
            id_chapter = novel_info.find("a").get("href")
        except:
            pass

        path_segment_novel = id_novel.split("/")[-1]
        path_segment_chapter = id_chapter.split("/")[-1]

        link_server_novel = make_link(localhost, f"/web/rnovel/4/{path_segment_novel}/")
        link_server_chapter = make_link(
            localhost, f"/web/rnovel/4/{path_segment_novel}/{path_segment_chapter}/"
        )

        novel_detail = {
            "id_novel": id_novel,
            "title_novel": title_novel,
            "poster_novel": poster_novel,
            "link_server_novel": link_server_novel,
            "id_chapter": id_chapter,
            "title_chapter": title_chapter,
            "link_server_chapter": link_server_chapter,
        }
        popular_novel.append(novel_detail)

    return popular_novel


def get_novel_server_4(path):
    BASE_LINK = "https://bestlightnovel.com/"
    link_novel = f"{BASE_LINK}{path}"
    localhost = split_join(request.url)
    request_novel = requests.get(link_novel)
    soup_novel = BeautifulSoup(request_novel.text, "html.parser")

    novel_info = soup_novel.find("ul", class_="truyen_info_right").find_all("li")

    title_novel = ""
    try:
        title_novel = novel_info[0].find("h1").text.strip()
    except:
        pass

    id_novel = link_novel

    author = ""
    try:
        author = novel_info[1].find("a").text.strip()
    except:
        pass

    status = ""
    try:
        status = novel_info[3].find("a").text.strip()
    except:
        pass

    catergories = ""
    try:
        catergories = [data.text.strip() for data in novel_info[2].find_all("a")]
    except:
        pass

    str_catergories = " ,".join(catergories)

    description = ""
    try:
        description = soup_novel.find("div", id="noidungm").text.strip()
    except:
        pass

    poster_novel = ""
    try:
        poster_novel = (
            soup_novel.find("div", class_="truyen_info_left").find("img").get("src")
        )
    except:
        pass

    list_chapter = soup_novel.find("div", class_="chapter-list").find_all(
        "div", class_="row"
    )
    chapters = {}
    name_chapters = []
    for chapter in list_chapter:
        name_chapter = chapter.find("a").text.strip()
        name_chapters.append(name_chapter)
        id_chapter = chapter.find("a").get("href")
        path_segment_chapter = id_chapter.split("/")[-1]
        link_server_chapter = make_link(
            localhost, f"/web/rnovel/4/{path}/{path_segment_chapter}/"
        )
        chapters[f"{name_chapter}"] = link_server_chapter

    novel_detail = {
        "genres": "novel",
        "id_novel": id_novel,
        "title_novel": title_novel,
        "poster": poster_novel,
        "description": description,
        "author": author,
        "catergories": str_catergories,
        "status": status,
        "chapters": chapters,
    }

    return novel_detail


def get_content_chapter_server_4(path, id_chapter):
    BASE_LINK = "https://bestlightnovel.com/"
    link_novel = f"{BASE_LINK}{path}/{id_chapter}"
    localhost = split_join(request.url)
    request_novel = requests.get(link_novel)
    soup_chapter = BeautifulSoup(request_novel.text, "html.parser")

    content_chapter = ""
    content = soup_chapter.find("div", id="vung_doc")
    try:
        for element in content.find_all(recursive=False):
            if element.name == "h3":
                content_chapter += element.text + "\n"
            elif element.name == "br":
                content_chapter += "\n"
            elif element.name == "p":
                content_chapter += element.text.strip() + "\n"
    except:
        pass

    title_novel = ""
    try:
        title_novel = (
            soup_chapter.find("div", class_="lem_bem_top").find("a").text.strip()
        )
    except:
        pass

    title_chapter = ""
    try:
        title_chapter = soup_chapter.find("h1", class_="name_chapter").text.strip()
    except:
        pass

    chapter_detail = {
        "title_novel": title_novel,
        "title_chapter": title_chapter,
        "content_chapter": content_chapter,
    }

    return chapter_detail
