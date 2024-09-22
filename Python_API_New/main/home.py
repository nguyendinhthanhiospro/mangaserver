from bs4 import BeautifulSoup
from wtforms import SubmitField
from main.form import SwitchForm
from main.model import LogUser
import requests
from . import *


def fix_title_chapter(url_chapter, url_manga):
    return "Chapter " + url_chapter.lstrip(url_manga)


def get_all_data_of_server(index, type):
    result = []
    all_data_of_server = (
        db.session.query(Manga_Update, List_Manga)
        .join(List_Manga, Manga_Update.id_manga == List_Manga.id_manga)
        .join(List_Server, List_Manga.id_server == List_Server.name_server)
        .filter((List_Server.index == index) & Manga_Update.id_manga.like(f"%{type}%"))
        .all()
    )

    for data in all_data_of_server:

        localhost = split_join(request.url)
        url = make_link(localhost, f"/r{type}/{data.Manga_Update.path_segment_manga}")
        data = {
            "url": url,
            "title_manga": data.Manga_Update.title_manga,
            "author": data.List_Manga.author,
            "categories": data.Manga_Update.categories,
            "image_poster_link_goc": data.Manga_Update.poster,
            "rate": data.Manga_Update.rate,
            "time_release": data.Manga_Update.time_release,
            "r18": check_r18(
                data.Manga_Update.categories + data.Manga_Update.title_manga
            ),
        }
        result.append(data)

    return result


def get_id_server(index):
    return List_Server.query.filter_by(index=index).first().name_server


def new_release_comics(index, limit, type):
    data_new_release_comics = []

    new_release = (
        db.session.query(Manga_Update, List_Manga)
        .join(List_Manga, Manga_Update.id_manga == List_Manga.id_manga)
        .join(List_Server, List_Manga.id_server == List_Server.name_server)
        .filter((List_Server.index == index) & Manga_Update.id_manga.like(f"%{type}%"))
        .order_by(Manga_Update.time_release.desc())
        .limit(limit)
    )

    for data in new_release:
        localhost = split_join(request.url)
        url_manga = make_link(
            localhost, f"/r{type}/{data.Manga_Update.path_segment_manga}"
        )
        url_chapter = make_link(
            localhost,
            f"/r{type}/{data.Manga_Update.path_segment_manga}/{data.Manga_Update.path_segment_chapter}",
        )
        
        data = {
            "url_manga": url_manga,
            "title_manga": data.List_Manga.title_manga,
            "author": data.List_Manga.author,
            "categories": data.List_Manga.categories,
            "image_poster_link_goc": data.Manga_Update.poster,
            "rate": data.Manga_Update.rate,
            "chapter_new": fix_title_chapter(url_chapter, url_manga),
            "url_chapter": url_chapter,
            "time_release": data.Manga_Update.time_release,
        }
        
        if r18_server_status() == "off":
            if check_r18(data["title_manga"]):
                continue
            if check_r18(data["categories"]):
                continue
        
        data_new_release_comics.append(data)

    return data_new_release_comics


# RECENT COMICS
def recent_comics(index, limit, type):
    data_recent_comics = []

    recent_comics = (
        db.session.query(Manga_Update, List_Manga)
        .join(List_Manga, Manga_Update.id_manga == List_Manga.id_manga)
        .join(List_Server, List_Manga.id_server == List_Server.name_server)
        .filter((List_Server.index == index) & Manga_Update.id_manga.like(f"%{type}%"))
        .order_by(Manga_Update.time_release.desc())
        .limit(limit)
    )  

    for recent_comic in recent_comics:

        localhost = split_join(request.url)
        data = {
            "url_manga": make_link(
                localhost,
                f"/r{type}/{recent_comic.Manga_Update.path_segment_manga}",
            ),
            "title_manga": recent_comic.Manga_Update.title_manga,
            "author": recent_comic.List_Manga.author,
            "categories": recent_comic.Manga_Update.categories,
            "image_poster_link_goc": recent_comic.Manga_Update.poster,
            "rate": recent_comic.Manga_Update.rate,
            "chapter_new": recent_comic.Manga_Update.path_segment_chapter,
            "url_chapter": make_link(
                localhost,
                f"/r{type}/{recent_comic.Manga_Update.path_segment_manga}/{recent_comic.Manga_Update.path_segment_chapter}",
            ),
            "time_release": recent_comic.Manga_Update.time_release,
            "path_segment_manga": recent_comic.Manga_Update.path_segment_manga,
        }
        
        if r18_server_status() == "off":
            if check_r18(data["title_manga"]):
                continue
            if check_r18(data["categories"]):
                continue
        
        data_recent_comics.append(data)

    return data_recent_comics


# RECOMMENDED COMICS
def recommended_comics(index, limit, type):
    data_recommended_comics = []

    recommended_comics = (
        db.session.query(Manga_Update, List_Manga)
        .join(List_Manga, Manga_Update.id_manga == List_Manga.id_manga)
        .join(List_Server, List_Manga.id_server == List_Server.name_server)
        .filter(
            (List_Server.index == index) & (Manga_Update.id_manga.like(f"%{type}%"))
        )
        .limit(limit)
    )

    for manga in recommended_comics:

        localhost = split_join(request.url)
        data = {
            "url_manga": make_link(
                localhost,
                f"/r{type}/{manga.Manga_Update.path_segment_manga}",
            ),
            "title_manga": manga.Manga_Update.title_manga,
            "author": manga.List_Manga.author,
            "categories": manga.Manga_Update.categories,
            "image_poster_link_goc": manga.Manga_Update.poster,
            "rate": manga.Manga_Update.rate,
            "chapter_new": manga.Manga_Update.path_segment_chapter,
            "url_chapter": make_link(
                localhost,
                f"/r{type}/{manga.Manga_Update.path_segment_manga}/{manga.Manga_Update.path_segment_chapter}",
            ),
            "time_release": manga.Manga_Update.time_release,
            "path_segment_manga": manga.Manga_Update.path_segment_manga,
        }
        
        if r18_server_status() == "off":
            if check_r18(data["title_manga"]):
                continue
            if check_r18(data["categories"]):
                continue
        
        data_recommended_comics.append(data)

    return data_recommended_comics


# COOMING SOON COMICS
def cooming_soon_comics(index, limit, type):
    data_cooming_soon_comics = []

    cooming_soon_comics = (
        db.session.query(Manga_Update, List_Manga)
        .join(List_Manga, Manga_Update.id_manga == List_Manga.id_manga)
        .join(List_Server, List_Manga.id_server == List_Server.name_server)
        .filter(
            (List_Server.index == index) & (Manga_Update.id_manga.like(f"%{type}%"))
        )
        .limit(limit)
    )
    
    for manga in cooming_soon_comics:
        localhost = split_join(request.url)
        data = {
            "title_manga": manga.Manga_Update.title_manga,
            "image_poster_link_goc": manga.Manga_Update.poster,
            "author": "AUTHOR",
            "categories": manga.Manga_Update.categories,
            "time_release": manga.Manga_Update.time_release,
            "url_manga": make_link(
                localhost,
                f"/r{type}/{manga.Manga_Update.path_segment_manga}",
            ),
        }
        
        if r18_server_status() == "off":
            if check_r18(data["title_manga"]):
                continue
            if check_r18(data["categories"]):
                continue
        
        data_cooming_soon_comics.append(data)
    
    return data_cooming_soon_comics


# BEST 15 COMICS WEEK
def best_15_comics_week(index, limit, type):
    data_best_15_comics_weeks = []

    best_15_comics_weeks = (
        db.session.query(Manga_Update, List_Manga)
        .join(List_Manga, Manga_Update.id_manga == List_Manga.id_manga)
        .join(List_Server, List_Manga.id_server == List_Server.name_server)
        .filter(
            (List_Server.index == index) & (Manga_Update.id_manga.like(f"%{type}%"))
        )
        .order_by(Manga_Update.views_week.desc())
        .limit(limit)
    )

    for manga in best_15_comics_weeks:

        localhost = split_join(request.url)
        data = {
            "url_manga": make_link(
                localhost,
                f"/r{type}/{manga.Manga_Update.path_segment_manga}",
            ),
            "title_manga": manga.Manga_Update.title_manga,
            "author": manga.List_Manga.author,
            "categories": manga.Manga_Update.categories,
            "image_poster_link_goc": manga.Manga_Update.poster,
            "rate": manga.Manga_Update.rate,
            "chapter_new": manga.Manga_Update.path_segment_chapter,
            "url_chapter": make_link(
                localhost,
                f"/r{type}/{manga.Manga_Update.path_segment_manga}/{manga.Manga_Update.path_segment_chapter}",
            ),
            "time_release": manga.Manga_Update.time_release,
            "path_segment_manga": manga.Manga_Update.path_segment_manga,
        }
        
        if r18_server_status() == "off":
            if check_r18(data["title_manga"]):
                continue
            if check_r18(data["categories"]):
                continue
        
        data_best_15_comics_weeks.append(data)

    return data_best_15_comics_weeks


# COMEDY COMMICS
def comedy_comics(index, limit, type):
    data_comedy_comics = []

    comedy_comics = (
        db.session.query(Manga_Update, List_Manga)
        .join(List_Manga, Manga_Update.id_manga == List_Manga.id_manga)
        .join(List_Server, List_Manga.id_server == List_Server.name_server)
        .filter(
            (List_Server.index == index)
            & (Manga_Update.categories.like(f"%comedy%"))
            & (Manga_Update.id_manga.like(f"%{type}%"))
        )
        .order_by(Manga_Update.time_release.desc())
        .limit(limit)
    )

    for manga in comedy_comics:

        localhost = split_join(request.url)
        data = {
            "id_manga": manga.List_Manga.id_manga,
            "url_manga": make_link(
                localhost, f"/r{type}/{manga.List_Manga.path_segment_manga}"
            ),
            "title_manga": manga.List_Manga.title_manga,
            "author": manga.List_Manga.author,
            "image_poster_link_goc": manga.List_Manga.poster_original,
            "categories": manga.List_Manga.categories,
            "rate": manga.List_Manga.rate,
            "time_release": manga.Manga_Update.time_release,
            "chaper_new": manga.Manga_Update.path_segment_chapter,
            "description": manga.List_Manga.descript_manga,
            "path_segment_manga": manga.Manga_Update.path_segment_manga,
        }
        
        if r18_server_status() == "off":
            if check_r18(data["title_manga"]):
                continue
            if check_r18(data["categories"]):
                continue
        
        data_comedy_comics.append(data)
        
    return data_comedy_comics


# FREE COMICS
def free_comics(index, limit, type):
    data_free_comics = []

    free_comics = (
        db.session.query(Manga_Update, List_Manga)
        .join(List_Manga, Manga_Update.id_manga == List_Manga.id_manga)
        .join(List_Server, List_Manga.id_server == List_Server.name_server)
        .filter(
            (List_Server.index == index) & (Manga_Update.id_manga.like(f"%{type}%"))
        )
        .order_by(Manga_Update.time_release.desc())
        .limit(limit)
    )
    
    for free_comic in free_comics:

        localhost = split_join(request.url)
        data = {
            "url_manga": make_link(
                localhost, f"/r{type}/{free_comic.Manga_Update.path_segment_manga}"
            ),
            "title_manga": free_comic.Manga_Update.title_manga,
            "author": free_comic.List_Manga.author,
            "categories": free_comic.Manga_Update.categories,
            "image_poster_link_goc": free_comic.Manga_Update.poster,
            "rate": free_comic.Manga_Update.rate,
            "chapter_new": free_comic.Manga_Update.path_segment_chapter,
            "url_chapter": make_link(
                localhost,
                f"/r{type}/{free_comic.Manga_Update.path_segment_manga}/{free_comic.Manga_Update.path_segment_chapter}",
            ),
            "time_release": free_comic.Manga_Update.time_release,
            "path_segment_manga": free_comic.Manga_Update.path_segment_manga,
        }
        
        if r18_server_status() == "off":
            if check_r18(data["title_manga"]):
                continue
            if check_r18(data["categories"]):
                continue
        
        data_free_comics.append(data)

    return data_free_comics


# NEWS
def anime_manga_news(limit):
    data_news = []
    news = Anime_Manga_News.query.limit(limit).all()
    localhost = split_join(request.url)
    for new in news:
        id_news = conver_url(new.idNews)
        data = {
            "id_news": id_news,
            "url_news": make_link(localhost, f"/news/{id_news}"),
            "title_news": new.title_news,
            "time_news": new.time_news,
            "images_poster": new.images_poster,
        }
        data_news.append(data)
    return data_news


# NEW USER
def user_new(limit):
    try:
        users = Users.query.order_by(desc(Users.time_register)).limit(limit)
        data_user = []
        if users:
            for user in users:
                profile = Profiles.query.filter(Profiles.id_user == user.id_user).first()
                if profile:
                    data = {
                        "id_user": user.id_user,
                        "name_user": profile.name_user,
                        "avatar_user": profile.avatar_user,
                        "participation_time": convert_time(user.time_register),
                    }
                    data_user.append(data)
        return data_user
    except:
        pass


# RANK WEEK
def rank_manga_week(index, limit, type):
    data_rank_manga_week = []

    rank_manga_week = (
        db.session.query(Manga_Update, List_Manga)
        .join(List_Manga, Manga_Update.id_manga == List_Manga.id_manga)
        .join(List_Server, List_Manga.id_server == List_Server.name_server)
        .filter(
            (List_Server.index == index) & (Manga_Update.id_chapter.like(f"%{type}%"))
        )
        .order_by(Manga_Update.views_week.desc())
        .limit(limit)
    )

    for rank in rank_manga_week:

        localhost = split_join(request.url)
        data = {
            "url_manga": make_link(
                localhost, f"/r{type}/{rank.List_Manga.path_segment_manga}"
            ),
            "title_manga": rank.List_Manga.title_manga,
            "author": rank.List_Manga.author,
            "image_poster_link_goc": rank.Manga_Update.poster,
            "categories": rank.List_Manga.categories,
            "views": rank.Manga_Update.views,
            "path_segment_manga": rank.Manga_Update.path_segment_manga,
        }
        
        if r18_server_status() == "off":
            if check_r18(data["title_manga"]):
                continue
            if check_r18(data["categories"]):
                continue
        
        data_rank_manga_week.append(data)

    return data_rank_manga_week


# RANK MONTH
def rank_manga_month(index, limit, type):
    data_rank_manga_month = []

    rank_manga_month = (
        db.session.query(Manga_Update, List_Manga)
        .join(List_Manga, Manga_Update.id_manga == List_Manga.id_manga)
        .join(List_Server, List_Manga.id_server == List_Server.name_server)
        .filter(
            (List_Server.index == index) & (Manga_Update.id_chapter.like(f"%{type}%"))
        )
        .order_by(Manga_Update.views_month.desc())
        .limit(limit)
    )

    for rank in rank_manga_month:

        localhost = split_join(request.url)
        data = {
            "url_manga": make_link(
                localhost, f"/r{type}/{rank.List_Manga.path_segment_manga}"
            ),
            "title_manga": rank.List_Manga.title_manga,
            "author": rank.List_Manga.author,
            "image_poster_link_goc": rank.Manga_Update.poster,
            "categories": rank.List_Manga.categories,
            "views": rank.Manga_Update.views,
            "path_segment_manga": rank.Manga_Update.path_segment_manga,
        }
        
        if r18_server_status() == "off":
            if check_r18(data["title_manga"]):
                continue
            if check_r18(data["categories"]):
                continue
        
        data_rank_manga_month.append(data)

    return data_rank_manga_month


# RANK YEAR
def rank_manga_year(index, limit, type):
    data_rank_manga_year = []

    rank_manga_year = (
        db.session.query(Manga_Update, List_Manga)
        .join(List_Manga, Manga_Update.id_manga == List_Manga.id_manga)
        .join(List_Server, List_Manga.id_server == List_Server.name_server)
        .filter(
            (List_Server.index == index) & (Manga_Update.id_chapter.like(f"%{type}%"))
        )
        .order_by(Manga_Update.views.desc())
        .limit(limit)
    )

    for rank in rank_manga_year:

        localhost = split_join(request.url)
        data = {
            "url_manga": make_link(
                localhost, f"/r{type}/{rank.List_Manga.path_segment_manga}"
            ),
            "title_manga": rank.List_Manga.title_manga,
            "author": rank.List_Manga.author,
            "image_poster_link_goc": rank.Manga_Update.poster,
            "categories": rank.List_Manga.categories,
            "views": rank.Manga_Update.views,
            "path_segment_manga": rank.Manga_Update.path_segment_manga,
        }
        
        if r18_server_status() == "off":
            if check_r18(data["title_manga"]):
                continue
            if check_r18(data["categories"]):
                continue
            
        data_rank_manga_year.append(data)
        
    return data_rank_manga_year


# COMMENTS
def comment_new(limit):
    data_comment_news = []
    rank_manga = (
        Manga_Update.query.order_by(Manga_Update.views.desc()).limit(limit).all()
    )
    for i, rank in enumerate(rank_manga):
        localhost = split_join(request.url)
        comment_new = (
            Comments.query.filter_by(path_segment_manga=rank.path_segment_manga)
            .order_by(
                func.STR_TO_DATE(Comments.time_comment, "%H:%i:%S %d-%m-%Y").desc()
            )
            .first()
        )
        if comment_new is None:
            continue
        profile = Profiles.query.get_or_404(comment_new.id_user)
        count_comment = Comments.query.filter_by(
            path_segment_manga=comment_new.path_segment_manga, is_comment_reply=False
        ).count()
        count_reply_comment = Comments.query.filter_by(
            path_segment_manga=comment_new.path_segment_manga, is_comment_reply=True
        ).count()
        data = {
            "id_user": comment_new.id_user,
            "name_user": profile.name_user,
            "avatar_user": profile.avatar_user,
            "id_comment": comment_new.id_comment,
            "content": comment_new.content,
            "time_comment": convert_time(comment_new.time_comment),
            "title_manga": rank.title_manga,
            "url_manga": make_link(
                localhost, f"/manga/{comment_new.path_segment_manga}"
            ),
            "count_comment": count_comment,
            "count_reply_comment": count_reply_comment,
        }
        data_comment_news.append(data)
    return data_comment_news


# REVIEWS MANGA
def reviews_manga(limit):
    data_reviews_manga = []
    reviews_manga = Reviews_Manga.query.limit(limit).all()

    for review in reviews_manga:
        data = {
            "idReview": review.idReview,
            "noi_dung": review.noi_dung,
            "link_manga": review.link_manga,
            "link_avatar_user_comment": review.link_avatar_user_comment,
            "link_user": review.link_user,
            "time_review": review.time_review,
        }
        data_reviews_manga.append(data)
    return data_reviews_manga


# REVIEWS ANIME
def reviews_anime(limit):
    data_reviews_anime = []
    reviews_manga = Reviews_Anime.query.limit(limit).all()
    for review in reviews_manga:
        data = {
            "idReview": review.idReview,
            "noi_dung": review.noi_dung,
            "link_anime": review.link_anime,
            "link_avatar_user_comment": review.link_avatar_user_comment,
            "link_user": review.link_user,
            "time_review": review.time_review,
        }
        data_reviews_anime.append(data)
    return data_reviews_anime


# CURRENTLY READING
def currently_reading(limit, type):
    list_manga = []
    added_list = []
    id_user = current_user.id_user
    log_user = (
        db.session.query(LogUser)
        .filter(
            (LogUser.id_user == id_user) & (Manga_Update.id_chapter.like(f"%{type}%"))
        )
        .order_by(LogUser.read_time.desc())
        .limit(limit)
    )

    for manga in log_user:
        title_manga = manga.title_manga
        if title_manga in added_list:
            pass
        else:
            localhost = split_join(request.url)
            data = {
                "url_manga": make_link(
                    localhost, f"/r{type}/{manga.path_segment_manga}/"
                ),
                "title_manga": manga.title_manga,
                "categories": manga.categories,
                "poster": manga.poster,
                "rate": manga.rate,
                "last_time_read": get_time_diff(
                    datetime.strptime(manga.read_time, "%H:%M:%S %d-%m-%Y"),
                    datetime.now(),
                ),
            }
            list_manga.append(data)
            added_list.append(title_manga)

    return list_manga

def get_lastest_manga(index, limit, type):
    lastest_manga = []
    
    list_lastest_manga = (
        db.session.query(Manga_Update, List_Manga)
        .join(List_Manga, Manga_Update.id_manga == List_Manga.id_manga)
        .join(List_Server, List_Manga.id_server == List_Server.name_server)
        .filter(
            (List_Server.index == index) & (Manga_Update.id_manga.like(f"%{type}%"))
        )
        .order_by(Manga_Update.time_release.desc())
        .limit(limit)
    )


    for manga in list_lastest_manga:

        chapter_new = ""
        url_chapter = ""
        try:
            chapter_info = List_Chapter.query.filter(List_Chapter.id_manga == manga.List_Manga.id_manga).order_by(desc(List_Chapter.time_release)).first()
            chapter_new = chapter_info.title_chapter
            url_chapter = make_link(
                localhost, f"/r{type}/{manga.List_Manga.path_segment_manga}/{chapter_info.path_segment_chapter}"
            )
        except:
            pass

        localhost = split_join(request.url)
        data = {
            "url_manga": make_link(
                localhost, f"/r{type}/{manga.List_Manga.path_segment_manga}"
            ),
            "title_manga": manga.List_Manga.title_manga,
            "author": manga.List_Manga.author,
            "image_poster_link_goc": manga.Manga_Update.poster,
            "categories": manga.List_Manga.categories,
            "views": manga.Manga_Update.views,
            "path_segment_manga": manga.Manga_Update.path_segment_manga,
            "time_release": manga.Manga_Update.time_release,
            "chapter_new": chapter_new,
            "url_chapter": url_chapter,
        }
        
        if r18_server_status() == "off":
            if check_r18(data["title_manga"]):
                continue
            if check_r18(data["categories"]):
                continue
            
        lastest_manga.append(data)
        
    return lastest_manga
