from main import *
from main.form import SwitchForm
from main.home import *
from main.home import comment_new, best_15_comics_week
import random

from main.server import *

list_of_web_server_lastest_update = {
    "1": get_lasted_manga_updates_server_1,
    "2": get_lasted_manga_updates_server_2,
    "3": get_lasted_manga_updates_server_3,
    "4": get_lasted_novel_updates_server_4,
    # "6": get_lasted_manga_updates_server_6,
    "7": get_lasted_manga_updates_server_7,
    "9": get_lasted_manga_updates_server_9,
    "12": get_lasted_manga_updates_server_12,
    "13": get_lasted_manga_updates_server_13,
    "14": get_lasted_manga_updates_server_14,
    "15": get_lasted_manga_updates_server_15,
    "16": get_lasted_manga_updates_server_16,
    "17": get_lasted_manga_updates_server_17,
    "18": get_lasted_manga_updates_server_18,
    "19": get_lasted_manga_updates_server_19,
}

list_of_web_server_popular = {
    "2": get_popular_manga_server_2,
    "4": get_popular_novel_server_4,
    "12": get_popular_manga_server_12,
    "19": get_popular_manga_server_19,
    }

list_of_web_server_hot = {
    "1": get_hot_manga_server_1,
    "3": get_hot_manga_server_3,
    "13": get_hot_manga_server_13,
    "14": get_hot_manga_server_14,
    "15": get_hot_manga_server_15,
    "16": get_hot_manga_server_16,
    "17": get_hot_manga_server_17,
    "18": get_hot_manga_server_18,
    }

@app.route("/<index>/<type>/<id_user>/")
def get_home(index, type, id_user):

    session["server"] = index

    # new_release_data = ""
    # if id_user == "0":
    #     new_release_data = {
    #         "id": 1,
    #         "type": 1,
    #         "name": "New Release Comics",
    #         "data": new_release_comics(index, 20, type),
    #     }
    # else:
    #     user = Users.query.get_or_404(id_user)
    #     if user.web_reading_mode_status == "on":
    #         # mangainn.net(index=0) dang chet, su dung data local cho index = 0
    #         if str(index) == "0":
    #             new_release_data = {
    #                 "id": 1,
    #                 "type": 1,
    #                 "name": "New Release Comics",
    #                 "data": new_release_comics(index, 20, type),
    #             }
    #         else:
    #             new_release_data = {
    #                 "id": 1,
    #                 "type": 1,
    #                 "name": "New Release Comics",
    #                 "data": list_of_web_server_lastest_update[index](),
    #             }
    #     else:
    #         new_release_data = {
    #             "id": 1,
    #             "type": 1,
    #             "name": "New Release Comics",
    #             "data": new_release_comics(index, 20, type),
    #         }
    new_release_data = {
            "id": 1,
            "type": 1,
            "name": "New Release Comics",
            "data": list_of_web_server_lastest_update[index](),
        }
    free_comics = []
    try:
        free_comics = random.sample(free_comics(index, 40, type), 12)
    except:
        pass

    result = [
        new_release_data,
        {
            "id": 2,
            "type": 1,
            "name": "Recent Comics",
            "data": recent_comics(index, 30, type),
        },
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
            "data": cooming_soon_comics(index, 10, type),
        },
        {
            "id": 5,
            "type": 1,
            "name": "Top 15 Best Comics Of The Week",
            "data": best_15_comics_week(index, 15, type),
        },
        {
            "id": 6,
            "type": 1,
            "name": "Comedy Comics",
            "data": comedy_comics(index, 24, type),
        },
        {
            "id": 7,
            "type": 1,
            "name": "Free Comics",
            "data": free_comics,
        },
        {"id": 8, "type": 2, "name": "Anime Manga News", "data": anime_manga_news(7)},
        {
            "id": 9,
            "type": 3,
            "name": "Rank Week",
            "data": rank_manga_week(index, 20, type),
        },
        {
            "id": 10,
            "type": 3,
            "name": "Rank Month",
            "data": rank_manga_month(index, 20, type),
        },
        {
            "id": 11,
            "type": 3,
            "name": "Rank Year",
            "data": rank_manga_year(index, 20, type),
        },
        {"id": 12, "type": 4, "name": "User New", "data": user_new(12)},
        {"id": 13, "type": 4, "name": "Comments", "data": comment_new(10)},
    ]

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


@app.route("/<index>/<type>/new_release_comics/<int:page>/<int:id_user>")
@cache.cached(timeout=60)
def see_all_new_release_comics(index, type, page, id_user):
    if id_user == 0:
        return separate_page(new_release_comics(index, None, type), page, type)
    
    check_mode = web_server_mode_status(id_user)
    if web_server_mode_status(id_user) == "on":
        print("_____mode_____", check_mode)
    else:
        return separate_page(new_release_comics(index, None, type), page, type)
    # return separate_page(list_of_web_server_lastest_update[index](), page)

@app.route("/<index>/<type>/recent_comics/<int:page>")
@cache.cached(timeout=60)
def see_all_recent_comics(index, type, page):
    return separate_page(recent_comics(index, None, type), page, type)


@app.route("/<index>/<type>/recommended_comics/<int:page>")
@cache.cached(timeout=60)
def see_all_recommended_comics(index, type, page):
    return separate_page(recommended_comics(index, 15, type), page, type)


@app.route("/<index>/<type>/cooming_soon_comics/<int:page>")
@cache.cached(timeout=60)
def see_all_cooming_soon_comics(index, type, page):
    return separate_page(cooming_soon_comics(index, None, type), page, type)


@app.route("/<index>/<type>/best_15_comics_week/<int:page>")
@cache.cached(timeout=60)
def see_all_best_15_comics_week(index, type, page):
    return separate_page(best_15_comics_week(index, 15, type), page, type)


@app.route("/<index>/<type>/comedy_comics/<int:page>")
@cache.cached(timeout=60)
def see_all_comedy_comics(index, type, page):
    return separate_page(comedy_comics(index, None, type), page, type)


@app.route("/<index>/<type>/free_comics/<int:page>")
@cache.cached(timeout=60)
def see_all_free_comics(index, type, page):
    return separate_page(free_comics(index, None, type), page, type)

@app.route("/<index>/<type>/lastest_manga/<int:page>")
@cache.cached(timeout=60)
def see_all_lastest_manga(index, type, page):
    return separate_page(get_lastest_manga(index, None, type), page, type)

@app.route("/anime_manga_news/")
@cache.cached(timeout=60)
def see_all_anime_manga_news():
    return anime_manga_news(None)


@app.route("/user_new/")
@cache.cached(timeout=60)
def see_all_user_new():
    return user_new(None)


@app.route("/<index>/<type>/rank_manga_week/<int:page>")
@cache.cached(timeout=600)
def see_all_rank_manga_week(index, type, page):
    return separate_page(rank_manga_week(index, None, type), page, type)


@app.route("/<index>/<type>/rank_manga_month/<int:page>")
@cache.cached(timeout=600)
def see_all_rank_manga_month(index, type, page):
    return separate_page(rank_manga_month(index, None, type), page, type)


@app.route("/<index>/<type>/rank_manga_year/<int:page>")
@cache.cached(timeout=600)
def see_all_rank_manga_year(index, type, page):
    return separate_page(rank_manga_year(index, None, type), page, type)


@app.route("/<index>/lastest_manga_updates/")
def see_lastest_manga_updates(index):
    return list_of_web_server_lastest_update[index]()

@app.route("/<index>/<type>/popular_manga/<int:page>")
def see_popular_manga(index, page, type):
    return separate_page(list_of_web_server_popular[index](), page, type)

@app.route("/<index>/<type>/hot_manga/<int:page>")
def see_hot_manga(index, page, type):
    return separate_page(list_of_web_server_hot[index](), page, type)

@app.route("/<index>/<type>/popular_manga/")
def see_all_popular_manga(index, type):
    return list_of_web_server_popular[index]()

@app.route("/<index>/<type>/hot_manga/")
def see_all_hot_manga(index, type):
    return list_of_web_server_hot[index]()

@app.route("/all-server")
def get_all_server():
    list_server = []
    unusable_list = [0, 5, 6, 7, 8, 9, 10, 11,]
    servers = List_Server.query.all()
    for server in servers:
        if int(server.index) not in unusable_list:
            server_name = server.name_server.replace('https:', '').replace('/','')
            list_server.append({'server_name': server_name, 'server_index': server.index, 'server_image': server.image_lang})
    return list_server


# @app.route("/server/<index>")
# def manga_of_server(index):
#     get_all_server()
#     result = List_Manga.query.filter_by(id_server=list_server[int(index)]).all()
#     print(result)
#     manga_list = [
#         {
#             "id_manga": manga.id_manga,
#             "title": manga.title_manga,
#             "description": manga.descript_manga,
#             "poster": manga.poster_original,
#             "categories": manga.categories,
#             "rate": manga.rate,
#             "views": manga.views_original,
#             "status": manga.status,
#             "author": manga.author,
#             "server": manga.id_server,
#         }
#         for manga in result
#     ]
#     return jsonify(manga_list)


@app.route("/currently-reading")
@login_required
def get_currently_reading():
    return currently_reading(None)
