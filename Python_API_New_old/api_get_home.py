from main import *
from main.form import SwitchForm
from main.home import (
    currently_reading,
    get_all_data_of_server,
    get_lasted_manga_updates_server_3,
    user_new,
    anime_manga_news,
    reviews_manga,
    reviews_anime,
    rank_manga_week,
    rank_manga_month,
    rank_manga_year,
)
from main.home import (
    comedy_comics,
    free_comics,
    cooming_soon_comics,
    recommended_comics,
    recent_comics,
    new_release_comics,
)
from main.home import comment_new, best_15_comics_week
import random

list_of_web_server_parse_code = {
    '3' : get_lasted_manga_updates_server_3,
}

@app.route("/<index>/<type>")
def get_home(index, type):
    
    session["server"] = index

    free_comics = []
    try:
        free_comics = random.sample(free_comics(index, 40, type), 12)
    except:
        pass

    result = [
        {
            "id": 1,
            "type": 1,
            "name": "New Release Comics",
            "data": new_release_comics(index, 20, type),
        },
        {"id": 2, "type": 1, "name": "Recent Comics", "data": recent_comics(index, 12, type)},
        {
            "id": 3,
            "type": 1,
            "name": "Recommended Comics",
            "data": recommended_comics(index, 30, type),
        },
        {
            "id": 4,
            "type": 1,
            "name": "Cooming Soon Comics",
            "data": cooming_soon_comics(index, 5, type),
        },
        {
            "id": 5,
            "type": 1,
            "name": "Top 15 Best Comics Of The Week",
            "data": best_15_comics_week(index, 15, type),
        },
        {"id": 6, "type": 1, "name": "Comedy Comics", "data": comedy_comics(index, 24, type)},
        {
            "id": 7,
            "type": 1,
            "name": "Free Comics",
            "data": free_comics,
        },
        {"id": 8, "type": 2, "name": "Anime Manga News", "data": anime_manga_news(7)},
        {"id": 9, "type": 3, "name": "Rank Week", "data": rank_manga_week(index, 20, type)},
        {
            "id": 10,
            "type": 3,
            "name": "Rank Month",
            "data": rank_manga_month(index, 20, type),
        },
        {"id": 11, "type": 3, "name": "Rank Year", "data": rank_manga_year(index, 20, type)},
        {"id": 12, "type": 4, "name": "User New", "data": user_new(12)},
        {"id": 13, "type": 4, "name": "Comments", "data": comment_new(10)},
    ]
    if current_user.is_authenticated:
        data = {
            "id": 14,
            "type": 1,
            "name": "Currently Reading",
            "data": currently_reading(50, type),
        }
        result.append(data)
    # if web_server_mode_status() == 'on':
    #     list_manga = list_of_web_server_parse_code[index]()
    #     data = {
    #         "id": 15,
    #         "type": 1,
    #         "name": "Lastest Manga Updates",
    #         "data": list_manga,
    #     }
    #     result.append(data)
    return result



@app.route("/news/<id_news>/")
def get_news(id_news):
    id_news = f"https://myanimelist.net/news/{id_news}"
    news = Anime_Manga_News.query.filter_by(idNews=id_news).first()
    if news is None:
        return jsonify(mgs="News do not exist!"), 404
    localhost = split_join(request.url)

    comment = []
    comment_news = Comment_News.query.filter_by(id_news=id_news).all()

    for comment_new in comment_news:
        id_user = 10
        profile = Profiles.query.filter_by(id_user=id_user).first()
        data_comment = {
            "id_comment": comment_new.id_comment,
            "id_user": id_user,
            "name_user": profile.name_user,
            "avatar_user": profile.avatar_user,
            "content": comment_new.comment,
            "time_comment": comment_new.time_comment,
            "likes": 0,
            "is_comment_reply": False,
            "is_edited_comment": False,
            "replies": [],
        }
        comment.append(data_comment)

    result = {
        "title_news": news.title_news,
        "images_poster": news.images_poster,
        "profile_user_post": make_link(localhost, f"/user/admin-fake"),
        "time_news": news.time_news,
        "category": news.category,
        "descript_pro": news.descript_pro,
        "comment": comment,
    }
    return jsonify(result)


@app.route("/<index>/<type>/new_release_comics/")
@cache.cached(timeout=60)
def see_all_new_release_comics(index, type):
    return new_release_comics(index, None, type)


@app.route("/<index>/<type>/recent_comics/")
@cache.cached(timeout=60)
def see_all_recent_comics(index, type):
    return recent_comics(index, None, type)


@app.route("/<index>/<type>/recommended_comics/")
@cache.cached(timeout=60)
def see_all_recommended_comics(index, type):
    return recommended_comics(index, None, type)


@app.route("/<index>/<type>/cooming_soon_comics/")
@cache.cached(timeout=60)
def see_all_cooming_soon_comics(index, type):
    return cooming_soon_comics(index, None, type)


@app.route("/<index>/<type>/best_15_comics_week/")
@cache.cached(timeout=60)
def see_all_best_15_comics_week(index, type):
    return best_15_comics_week(index, None, type)


@app.route("/<index>/<type>/comedy_comics/")
@cache.cached(timeout=60)
def see_all_comedy_comics(index, type):
    return comedy_comics(index, None, type)


@app.route("/<index>/<type>/free_comics/")
@cache.cached(timeout=60)
def see_all_free_comics(index, type):
    return free_comics(index, None, type)


@app.route("/anime_manga_news/")
@cache.cached(timeout=60)
def see_all_anime_manga_news():
    return anime_manga_news(None)


@app.route("/user_new/")
@cache.cached(timeout=60)
def see_all_user_new():
    return user_new(None)


@app.route("/<index>/<type>/rank_manga_week/")
@cache.cached(timeout=600)
def see_all_rank_manga_week(index, type):
    return rank_manga_week(index, None, type)


@app.route("/<index>/<type>/rank_manga_month/")
@cache.cached(timeout=600)
def see_all_rank_manga_month(index, type):
    return rank_manga_month(index, None, type)


@app.route("/<index>/<type>/rank_manga_year/")
@cache.cached(timeout=600)
def see_all_rank_manga_year(index, type):
    return rank_manga_year(index, None)

@app.route("/<index>/lastest_manga_updates/")
def see_lastest_manga_updates(index):
    return list_of_web_server_parse_code[index]()

list_server = []

@app.route("/all-server")
def get_all_server():
    result = List_Manga.query.all()
    for manga in result:
        if manga.id_server not in list_server:
            list_server.append(manga.id_server)
    return jsonify(list_server)


@app.route("/server/<index>")
def manga_of_server(index):
    get_all_server()
    result = List_Manga.query.filter_by(id_server=list_server[int(index)]).all()
    manga_list = [
        {
            "id_manga": manga.id_manga,
            "title": manga.title_manga,
            "description": manga.descript_manga,
            "poster": manga.poster_original,
            "categories": manga.categories,
            "rate": manga.rate,
            "views": manga.views_original,
            "status": manga.status,
            "author": manga.author,
            "server": manga.id_server,
        }
        for manga in result
    ]
    return jsonify(manga_list)


@app.route("/currently-reading")
@login_required
def get_currently_reading():
    return currently_reading(None)

