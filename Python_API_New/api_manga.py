from bs4 import BeautifulSoup
from flask import redirect
from flask_cors import cross_origin
import urllib.parse
from main import *
from main.form import SearchForm
from main.home import get_all_data_of_server, get_id_server
from main.model import Content_Chapter, LogUser
from main.server import *

list_api_from_server = {
    "1": [get_manga_server_1, get_image_chapter_server_1],
    "2": [get_manga_server_2, get_image_chapter_server_2],
    "3": [get_manga_server_3, get_image_chapter_server_3],
    "4": [get_novel_server_4, get_content_chapter_server_4],
    "6": [get_manga_server_6, get_image_chapter_server_6],
    "7": [get_manga_server_7, get_image_chapter_server_7],
    "9": [get_manga_server_9, get_image_chapter_server_9],
    "12": [get_manga_server_12, get_image_chapter_server_12],
    "13": [get_manga_server_13, get_image_chapter_server_13],
    "14": [get_manga_server_14, get_image_chapter_server_14],
    "15": [get_manga_server_15, get_image_chapter_server_15],
    "16": [get_manga_server_16, get_image_chapter_server_16],
    "17": [get_manga_server_17, get_image_chapter_server_17],
    "18": [get_manga_server_18, get_image_chapter_server_18],
    "19": [get_manga_server_19, get_image_chapter_server_19],
}


@app.route("/<index>/rmanga/<path_segment_manga>/")
@cross_origin(origin="*")
def get_manga(index, path_segment_manga):
    id_server = get_id_server(index)
    print("__path_segment_manga___" + str(path_segment_manga))
    manga = List_Manga.query.filter_by(
        path_segment_manga=path_segment_manga, id_server=id_server
    ).first()
    if manga is None:
        return jsonify(msg="Manga does not exist!"), 404

    localhost = split_join(request.url)
    chapters = list_chapter(localhost, manga.id_manga, path_segment_manga, "manga")
    if "novel" in manga.id_manga:
        manga.genres = "Novel"
    else:
        manga.genres = "Manga"

    manga_info = {
        "genres": manga.genres,
        "id_manga": manga.id_manga,
        "title": manga.title_manga,
        "description": manga.descript_manga,
        "poster": manga.poster_original,
        "categories": manga.categories,
        "rate": manga.rate,
        "views": manga.views_original,
        "status": manga.status,
        "author": manga.author,
        "comments": get_comments(path_segment_manga),
        "chapters": chapters,
        "server": manga.id_server,
        "r18": check_r18(manga.categories),
    }
    all_review = Reviews_Manga.query.all()
    review_of_manga = None
    for review in all_review:
        if (
            convert_title_manga(review.link_manga).lower()
            == str(manga.title_manga).lower()
        ):
            review_of_manga = Reviews_Manga.query.filter(
                Reviews_Manga.idReview == review.idReview
            ).first()
            break
    if review_of_manga is None:
        review_info = {"Err": "don't have review"}
    else:
        review_info = {
            "link_user": review_of_manga.link_user,
            "link_avatar_user": review_of_manga.link_avatar_user_comment,
            "link_manga": review_of_manga.link_manga,
            "noi_dung": review_of_manga.noi_dung,
            "time_release": review_of_manga.time_review,
        }
    return jsonify(manga_info, review_info)


@app.route("/<index>/rnovel/<path_segment_manga>/")
@cross_origin(origin="*")
def get_novel(index, path_segment_manga):
    id_server = get_id_server(index)

    manga = List_Manga.query.filter_by(
        path_segment_manga=path_segment_manga, id_server=id_server
    ).first()
    if manga is None:
        return jsonify(msg="Novel does not exist!"), 404

    localhost = split_join(request.url)
    chapters = list_chapter(localhost, manga.id_manga, path_segment_manga, "novel")

    if "novel" in manga.id_manga:
        manga.genres = "Novel"
    else:
        manga.genres = "Manga"
    manga_info = {
        "genres": manga.genres,
        "id_manga": manga.id_manga,
        "title": manga.title_manga,
        "description": manga.descript_manga,
        "poster": manga.poster_original,
        "categories": manga.categories,
        "rate": manga.rate,
        "views": manga.views_original,
        "status": manga.status,
        "author": manga.author,
        "comments": get_comments(path_segment_manga),
        "chapters": chapters,
        "server": manga.id_server,
        "r18": check_r18(manga.categories),
    }
    all_review = Reviews_Manga.query.all()
    review_of_manga = None
    for review in all_review:
        if (
            convert_title_manga(review.link_manga).lower()
            == str(manga.title_manga).lower()
        ):
            review_of_manga = Reviews_Manga.query.filter(
                Reviews_Manga.idReview == review.idReview
            ).first()
            break
    if review_of_manga is None:
        review_info = {"Err": "don't have review"}
    else:
        review_info = {
            "link_user": review_of_manga.link_user,
            "link_avatar_user": review_of_manga.link_avatar_user_comment,
            "link_manga": review_of_manga.link_manga,
            "noi_dung": review_of_manga.noi_dung,
            "time_release": review_of_manga.time_review,
        }
    return jsonify(manga_info, review_info)


@app.route("/rmanga/<path>")
@cross_origin(origin="*")
def dmc(path):
    try:
        print("___path___" + str(path))
        manga = List_Manga.query.filter_by(path_segment_manga=path).first()
        if manga is None:
            return jsonify(msg="Manga does not exist!"), 404

        localhost = split_join(request.url)
        chapters = list_chapter(localhost, manga.id_manga, path, "manga")
        print("_____________PRINT__chapters___" + str(chapters))
        if "novel" in manga.id_manga:
            manga.genres = "novel"
        else:
            manga.genres = "manga"

        manga_info = {
            "genres": manga.genres,
            "id_manga": manga.id_manga,
            "title": manga.title_manga,
            "description": manga.descript_manga,
            "poster": manga.poster_original,
            "categories": manga.categories,
            "rate": manga.rate,
            "views": manga.views_original,
            "status": manga.status,
            "author": manga.author,
            "comments": get_comments(path),
            "chapters": chapters,
        }
        all_review = Reviews_Manga.query.all()
        review_of_manga = None
        for review in all_review:
            if (
                convert_title_manga(review.link_manga).lower()
                == str(manga.title_manga).lower()
            ):
                review_of_manga = Reviews_Manga.query.filter(
                    Reviews_Manga.idReview == review.idReview
                ).first()
                break
        if review_of_manga is None:
            review_info = {"Err": "don't have review"}
        else:
            review_info = {
                "link_user": review_of_manga.link_user,
                "link_avatar_user": review_of_manga.link_avatar_user_comment,
                "link_manga": review_of_manga.link_manga,
                "noi_dung": review_of_manga.noi_dung,
                "time_release": review_of_manga.time_review,
            }
        return manga_info
    except Exception as e:
        print(e)
        return jsonify({"errMsg": "Internal Server Error"}, {"errCode": str(e)}), 500


@app.route("/rnovel/<path>")
@cross_origin(origin="*")
def dmc2(path):
    try:
        novel = List_Manga.query.filter_by(path_segment_manga=path).first()
        if novel is None:
            return jsonify(msg="Novel does not exist!"), 404

        localhost = split_join(request.url)
        chapters = list_chapter(localhost, novel.id_manga, path, "novel")

        manga_info = {
            "genres": "novel",
            "id_manga": novel.id_manga,
            "title": novel.title_manga,
            "description": novel.descript_manga,
            "poster": novel.poster_original,
            "categories": novel.categories,
            "rate": novel.rate,
            "views": novel.views_original,
            "status": novel.status,
            "author": novel.author,
            "comments": get_comments(path),
            "chapters": chapters,
        }
        all_review = Reviews_Manga.query.all()
        review_of_manga = None
        for review in all_review:
            if (
                convert_title_manga(review.link_manga).lower()
                == str(novel.title_manga).lower()
            ):
                review_of_manga = Reviews_Manga.query.filter(
                    Reviews_Manga.idReview == review.idReview
                ).first()
                break
        if review_of_manga is None:
            review_info = {"Err": "don't have review"}
        else:
            review_info = {
                "link_user": review_of_manga.link_user,
                "link_avatar_user": review_of_manga.link_avatar_user_comment,
                "link_manga": review_of_manga.link_manga,
                "noi_dung": review_of_manga.noi_dung,
                "time_release": review_of_manga.time_review,
            }
        return jsonify(manga_info, review_info)
    except Exception as e:
        print(e)
        return jsonify({"errMsg": "Internal Server Error"}, {"errCode": str(e)}), 500


@app.route("/rmanga/<path_segment_manga>/<path_segment_chapter>/")
@cross_origin(origin="*")
def get_image_chapter(path_segment_manga, path_segment_chapter):
    path_segment = f"{path_segment_manga}-{path_segment_chapter}"
    chapters = Imaga_Chapter.query.filter_by(path_segment=path_segment).first()

    if chapters is None:
        return jsonify(msg="NONE"), 404

    image_chapter = chapters.image_chapter_original.split(",")
    chapter = List_Chapter.query.filter_by(id_chapter=chapters.id_chapter).first()
    manga = Manga_Update.query.filter_by(id_manga=chapter.id_manga).first()

    manga.views_week += 1
    manga.views_month += 1
    manga.views += 1
    db.session.commit()

    chapter_info = {
        "title": manga.title_manga,
        "image_chapter": image_chapter,
        "chapter_name": path_segment_chapter,
    }

    return jsonify(chapter_info)


@app.route("/rnovel/<path_segment_manga>/<path_segment_chapter>/")
@cross_origin(origin="*")
def get_content_chapter(path_segment_manga, path_segment_chapter):
    path_segment = f"{path_segment_manga}-{path_segment_chapter}"
    novel = Manga_Update.query.filter_by(path_segment_manga=path_segment_manga).first()
    chapter = Content_Chapter.query.filter_by(path_segment=path_segment).first()
    if chapter is None:
        return jsonify(msg="NONE"), 404

    content_chapter = chapter.content_chapter

    novel.views_week += 1
    novel.views_month += 1
    novel.views += 1
    db.session.commit()

    chapter_info = {
        "title": novel.title_manga,
        "content": content_chapter,
        "chapter_name": path_segment_chapter,
    }
    return jsonify(chapter_info)


# GET COMMENT CHAPTER
@app.route("/cmanga/<path_segment_manga>/<path_segment_chapter>/")
def get_comment_chapter(path_segment_manga, path_segment_chapter):

    manga = List_Manga.query.filter_by(path_segment_manga=path_segment_manga).first()
    if manga is None:
        return jsonify(message="Manga not found"), 404

    chapter = List_Chapter.query.filter_by(
        id_manga=manga.id_manga, path_segment_chapter=path_segment_chapter
    ).first()

    if chapter is None:
        return jsonify(message="Chapter not found"), 404

    comments = (
        db.session.query(Comments)
        .filter_by(
            path_segment_manga=path_segment_manga,
            path_segment_chapter=path_segment_chapter,
        )
        .order_by(func.STR_TO_DATE(Comments.time_comment, "%H:%i:%S %d-%m-%Y").desc())
        .all()
    )
    if comments is None:
        return jsonify(message="There is no comment for this chapter/manga")

    result = []

    for comment in comments:
        like_count = LikesComment.query.filter_by(
            id_comment=comment.id_comment, status="like"
        ).count()
        profile = Profiles.query.filter_by(id_user=comment.id_user).first()
        if comment.is_comment_reply == 0:
            data = {
                "id_user": profile.id_user,
                "name_user": profile.name_user,
                "avatar_user": profile.avatar_user,
                "id_comment": comment.id_comment,
                "content": comment.content,
                "like_count": like_count,
                "time_comment": comment.time_comment,
                "is_edited_comment": comment.is_edited_comment,
                "replied_comment": [],
            }
            result.append(data)
    print(result)
    for comment in comments:
        if comment.is_comment_reply == 1:
            like_count = LikesComment.query.filter_by(
                id_comment=comment.id_comment, status="like"
            ).count()
            profile = Profiles.query.filter_by(id_user=comment.id_user).first()
            replied_comment = {
                "id_user": profile.id_user,
                "name_user": profile.name_user,
                "avatar_user": profile.avatar_user,
                "id_comment": comment.id_comment,
                "like_count": like_count,
                "content": comment.content,
                "time_comment": comment.time_comment,
                "is_edited_comment": comment.is_edited_comment,
            }
        for data in result:
            if data["id_comment"] == comment.reply_id_comment:
                data["replied_comment"].append(replied_comment)

    return jsonify(result)


# COMMENT CHAPTER MANGA
@app.route(
    "/cmanga/<path_segment_manga>/<path_segment_chapter>/<id_user>/", methods=["POST"]
)
def comment_chapter(path_segment_manga, path_segment_chapter, id_user):
    form = CommentsForm()
    id_user = id_user
    profile = Profiles.query.get_or_404(id_user)

    manga = List_Manga.query.filter_by(path_segment_manga=path_segment_manga).first()
    if manga is None:
        return jsonify(message="Manga not found"), 404

    chapter = List_Chapter.query.filter_by(
        id_manga=manga.id_manga, path_segment_chapter=path_segment_chapter
    ).first()
    if chapter is None:
        return jsonify(message="Chapter not found"), 404

    if form.validate_on_submit():
        content = form.content.data

        time = datetime.now().strftime("%H:%M:%S %d-%m-%Y")
        comment = Comments(
            id_user=id_user,
            path_segment_manga=path_segment_manga,
            path_segment_chapter=path_segment_chapter,
            content=content,
            time_comment=time,
        )
        profile.number_comments += 1
        db.session.add(comment)
        db.session.commit()
        comment = (
            db.session.query(Comments)
            .filter_by(
                id_user=id_user,
                path_segment_manga=path_segment_manga,
                path_segment_chapter=path_segment_chapter,
                content=content,
            )
            .first()
        )

        responses = {
            "id_comment": comment.id_comment,
            "id_user": id_user,
            "name_user": profile.name_user,
            "avatar_user": profile.avatar_user,
            "chapter": path_segment_chapter,
            "content": content,
            "time_comment": convert_time(time),
        }
        return jsonify(responses=responses)
    return jsonify(error=form.errors), 400


# GET COMMENT MANGA
@app.route("/cmanga/<path_segment_manga>/")
def get_comment_manga(path_segment_manga):
    return get_comments(path_segment_manga)


# COMMENT MANGA
@app.route("/cmanga/<path_segment_manga>/<int:id_user>/", methods=["POST"])
def comment_manga(path_segment_manga, id_user):
    form = CommentsForm()
    id_user = id_user
    profile = Profiles.query.get_or_404(id_user)

    manga = List_Manga.query.filter_by(path_segment_manga=path_segment_manga).first()
    if manga is None:
        return jsonify(message="Manga not found"), 404

    if form.validate_on_submit():
        content = form.content.data

        path_segment_chapter = "NONE"

        time = datetime.now().strftime("%H:%M:%S %d-%m-%Y")
        comment = Comments(
            id_user=id_user,
            path_segment_manga=path_segment_manga,
            path_segment_chapter=path_segment_chapter,
            content=content,
            time_comment=time,
        )
        profile.number_comments += 1
        db.session.add(comment)
        db.session.commit()
        responses = {
            "id_user": id_user,
            "name_user": profile.name_user,
            "avatar_user": profile.avatar_user,
            "chapter": path_segment_chapter,
            "content": content,
            "time_comment": convert_time(time),
        }
        return jsonify(responses=responses)
    return jsonify(error=form.errors), 400


@app.route("/reply-comment/<int:id_user>/<int:id_comment>/", methods=["POST"])
# @login_required
def reply_comments(id_user, id_comment):
    form = CommentsForm()
    profile = Profiles.query.get_or_404(id_user)
    comments = Comments.query.get_or_404(id_comment)
    if form.validate_on_submit():
        content = form.content.data
        time = datetime.now().strftime("%H:%M:%S %d-%m-%Y")

        comment = Comments(
            id_user=id_user,
            content=content,
            time_comment=time,
            path_segment_manga=comments.path_segment_manga,
            path_segment_chapter=comments.path_segment_chapter,
            is_comment_reply=True,
            reply_id_comment=id_comment,
        )

        db.session.add(comment)
        db.session.commit()
        comment_data = (
            db.session.query(Comments)
            .filter_by(
                id_user=id_user,
                path_segment_manga=comment.path_segment_manga,
                path_segment_chapter=comment.path_segment_chapter,
                content=content,
            )
            .first()
        )
        responses = {
            "id_comment": comment_data.id_comment,
            "id_user": id_user,
            "name_user": profile.name_user,
            "avatar_user": profile.avatar_user,
            "content": content,
            "chapter": comments.path_segment_chapter,
            "time_comment": convert_time(time),
            "is_comment_reply": True,
            "reply_id_comment": id_comment,
        }
        return jsonify(responses=responses)
    return jsonify(error=form.errors), 400


@app.route("/delete-comment/<id_comment>/", methods=["DELETE"])
def delete_comment(id_comment):
    id_user = current_user.id_user
    comment = Comments.query.get_or_404(id_comment)

    if comment.id_user != id_user:
        return jsonify(error="You do not have permission to delete comment"), 400

    comment_diary = CommentDiary(
        id_comment=comment.id_comment,
        content=comment.content,
        comment_type="delete",
        time_comment=comment.time_comment,
    )
    db.session.add(comment_diary)

    LikesComment.query.filter_by(id_comment=id_comment).delete()

    delete_reply_comment(comment)
    db.session.delete(comment)
    db.session.commit()
    return jsonify(message="Comment deleted successfully")


@app.route("/edit-comment/<id_comment>/", methods=["PATCH"])
@login_required
def edit_comments(id_comment):
    form = CommentsForm()
    id_user = current_user.id_user
    profile = Profiles.query.get_or_404(id_user)
    comments = Comments.query.get_or_404(id_comment)

    if comments.id_user != id_user:
        return jsonify(error="You do not have permission to edit comment"), 400

    if form.validate_on_submit():
        content = form.content.data
        time = datetime.now().strftime("%H:%M:%S %d-%m-%Y")

        if comments.is_edited_comment == False:
            comment = CommentDiary(
                id_comment=id_comment,
                content=comments.content,
                comment_type="before",
                time_comment=comments.time_comment,
            )
            db.session.add(comment)
            db.session.commit()

        comments.content = content
        edit_comment = CommentDiary(
            id_comment=id_comment,
            content=content,
            comment_type="after",
            time_comment=time,
        )
        db.session.add(edit_comment)

        comments.is_edited_comment = True
        db.session.commit()
        responses = {
            "id_user": id_user,
            "name_user": profile.name_user,
            "avatar_user": profile.avatar_user,
            "chapter": comments.path_segment_chapter,
            "content_update": content,
            "time_comment": convert_time(comments.time_comment),
        }
        return jsonify(responses=responses)
    return jsonify(error=form.errors), 400


@app.route("/comment-diary/<id_comment>/")
@login_required
def comments_diary(id_comment):
    id_user = current_user.id_user
    profile = Profiles.query.get_or_404(id_user)
    comment = Comments.query.get_or_404(id_comment)
    comments = (
        CommentDiary.query.filter_by(id_comment=id_comment)
        .order_by(
            func.STR_TO_DATE(CommentDiary.time_comment, "%H:%i:%S %d-%m-%Y").asc()
        )
        .all()
    )
    responses = []
    for comm in comments:
        result = {
            "id_user": id_user,
            "name_user": profile.name_user,
            "avatar_user": profile.avatar_user,
            "chapter": comment.path_segment_chapter,
            "content": comm.content,
            "time_comment": convert_time(comm.time_comment),
        }
        responses.append(result)
    return jsonify(CommentDiary=responses)


@app.route("/like-comment/<int:id_user>/<int:id_comment>/", methods=["POST", "PATCH"])
# @login_required
def like_comment(id_user, id_comment):
    like_status = LikesComment.query.filter_by(
        id_comment=id_comment, id_user=id_user
    ).first()
    comment = Comments.query.filter_by(id_comment=id_comment).first()
    if not comment:
        return jsonify(message="Comment does not exist!"), 404
    if like_status:
        if like_status.status == "like":
            like_status.status = "unlike"
            db.session.commit()
            return jsonify(message="Unliked Comment  successfully")
        else:
            like_status.status = "like"
            db.session.commit()
            return jsonify(message="Liked comment successfully")
    else:
        new_like = LikesComment(id_comment=id_comment, id_user=id_user, status="like")
        db.session.add(new_like)
        db.session.commit()
        return jsonify(message="Liked comment successfully")


@app.route("/manga-categories/<category>")
def manga_categories(category):
    result = []
    if category.find("Harem") == -1:
        mangas = (
            db.session.query(List_Manga, Manga_Update)
            .join(List_Manga)
            .filter(Manga_Update.categories.like(f"%{category}%"))
            .order_by(Manga_Update.time_release.desc())
            .all()
        )
        for manga in mangas:
            manga_info = {
                "id_manga": manga.List_Manga.id_manga,
                "title": manga.List_Manga.title_manga,
                "poster": manga.List_Manga.poster_original,
                "categories": manga.List_Manga.categories,
                "rate": manga.List_Manga.rate,
                "time_release": manga.Manga_Update.time_release,
                "chaper_new": manga.Manga_Update.id_chapter,
                "description": manga.List_Manga.descript_manga,
                "category": category.capitalize(),
            }
            result.append(manga_info)
    return jsonify(result)


@app.route("/manga-categories")
def get_all_categories():
    all_categories = []
    result = List_Category.query.all()
    for category in result:
        data = {
            "category_name": category.category_name,
            "decription": category.description,
            "image": category.image,
        }
        all_categories.append(data)

    return jsonify(all_categories)


@app.route("/search-manga", methods=["POST"])
def search_manga():
    form = SearchForm()
    if form.validate_on_submit():
        key = form.content.data
        result = (
            db.session.query(List_Manga, Manga_Update)
            .join(Manga_Update)
            .filter(List_Manga.title_manga.like(f"%{key}%"))
            .order_by(Manga_Update.time_release.desc())
            .all()
        )
        manga_list = [
            {
                "id_manga": manga.List_Manga.id_manga,
                "title": manga.List_Manga.title_manga,
                "description": manga.List_Manga.descript_manga,
                "poster": manga.List_Manga.poster_original,
                "categories": manga.List_Manga.categories,
                "rate": manga.List_Manga.rate,
                "views": manga.List_Manga.views_original,
                "status": manga.List_Manga.status,
                "time": manga.Manga_Update.time_release,
                "author": manga.List_Manga.author,
            }
            for manga in result
        ]
        if result is None:
            return jsonify(msg="Manga does not exist!"), 404
        return jsonify(manga_list)
    return jsonify(error=form.errors), 400


@app.route("/get-all-data-of-sever/<index>/<type>")
def get_all_data(index, type):
    return get_all_data_of_server(index=index, type=type)


@app.route("/search-manga-by-name-in-sever/<index>", methods=["POST"])
def search_manga_by_name_in_server(index):
    localhost = split_join(request.url)
    form = SearchForm()
    if form.validate_on_submit():
        key = form.content.data
        result = []
        mangas = (
            db.session.query(Manga_Update, List_Manga)
            .join(List_Manga, Manga_Update.id_manga == List_Manga.id_manga)
            .join(List_Server, List_Manga.id_server == List_Server.name_server)
            .filter((List_Manga.title_manga.like(f"%{key}%")))
            .all()
        )

        for manga in mangas:

            if r18_server_status() == "off":
                if check_r18(
                    manga.List_Manga.categories + manga.List_Manga.title_manga
                ):
                    continue
            server = List_Server.query.filter(
                List_Server.name_server == manga.List_Manga.id_server
            ).first()
            server_index = server.index
            path_segment_manga = manga.List_Manga.path_segment_manga
            link_manga = make_link(
                localhost, f"/{server_index}/rmanga/{path_segment_manga}"
            )
            data = {
                "id_manga": link_manga,
                "title": manga.List_Manga.title_manga,
                "description": manga.List_Manga.descript_manga,
                "poster": manga.List_Manga.poster_original,
                "categories": manga.List_Manga.categories,
                "rate": manga.List_Manga.rate,
                "views": manga.List_Manga.views_original,
                "status": manga.List_Manga.status,
                "time": manga.Manga_Update.time_release,
                "author": manga.List_Manga.author,
                "id_server": server_index,
            }
            result.append(data)

        if mangas is None:
            return jsonify(msg="Manga does not exist!"), 404
        return jsonify(result)
    return jsonify(error=form.errors), 400


@app.route("/search-manga-by-author-in-sever/<index>", methods=["POST"])
def search_manga_by_author_in_server(index):
    form = SearchForm()
    localhost = split_join(request.url)
    if form.validate_on_submit():
        key = form.content.data
        result = []
        mangas = (
            db.session.query(Manga_Update, List_Manga)
            .join(List_Manga, Manga_Update.id_manga == List_Manga.id_manga)
            .join(List_Server, List_Manga.id_server == List_Server.name_server)
            .filter((List_Server.index == index) & (List_Manga.author.like(f"%{key}%")))
            .all()
        )

        for manga in mangas:

            if r18_server_status() == "off":
                if check_r18(
                    manga.List_Manga.categories + manga.List_Manga.title_manga
                ):
                    continue

            path_segment_manga = manga.List_Manga.path_segment_manga
            link_manga = make_link(localhost, f"/{index}/rmanga/{path_segment_manga}")
            data = {
                "id_manga": link_manga,
                "title": manga.List_Manga.title_manga,
                "description": manga.List_Manga.descript_manga,
                "poster": manga.List_Manga.poster_original,
                "categories": manga.List_Manga.categories,
                "rate": manga.List_Manga.rate,
                "views": manga.List_Manga.views_original,
                "status": manga.List_Manga.status,
                "time": manga.Manga_Update.time_release,
                "author": manga.List_Manga.author,
                "id_server": manga.List_Manga.id_server,
            }
            result.append(data)

        if mangas is None:
            return jsonify(msg="Manga does not exist!"), 404
        return jsonify(result)
    return jsonify(error=form.errors), 400


@app.route("/search-manga-by-genre-in-sever/<index>", methods=["POST"])
def search_manga_by_genre_in_server(index):
    form = SearchForm()
    localhost = split_join(request.url)
    if form.validate_on_submit():
        key = form.content.data
        result = []
        mangas = (
            db.session.query(Manga_Update, List_Manga)
            .join(List_Manga, Manga_Update.id_manga == List_Manga.id_manga)
            .join(List_Server, List_Manga.id_server == List_Server.name_server)
            .filter(
                (List_Server.index == index) & (List_Manga.categories.like(f"%{key}%"))
            )
            .all()
        )

        for manga in mangas:

            if r18_server_status() == "off":
                if check_r18(
                    manga.List_Manga.categories + manga.List_Manga.title_manga
                ):
                    continue
            path_segment_manga = manga.List_Manga.path_segment_manga
            link_manga = make_link(localhost, f"/{index}/rmanga/{path_segment_manga}")
            data = {
                "id_manga": link_manga,
                "title": manga.List_Manga.title_manga,
                "description": manga.List_Manga.descript_manga,
                "poster": manga.List_Manga.poster_original,
                "categories": manga.List_Manga.categories,
                "rate": manga.List_Manga.rate,
                "views": manga.List_Manga.views_original,
                "status": manga.List_Manga.status,
                "time": manga.Manga_Update.time_release,
                "author": manga.List_Manga.author,
                "id_server": manga.List_Manga.id_server,
            }
            result.append(data)

        if mangas is None:
            return jsonify(msg="Manga does not exist!"), 404
        return jsonify(result)
    return jsonify(error=form.errors), 400


@app.route("/mode/web-server/<id_user>/")
def web_server_mode(id_user):
    user = Users.query.get_or_404(id_user)
    # index = session["server"]
    index = 1
    if user.web_reading_mode_status == "on":
        user.web_reading_mode_status = "off"
        db.session.commit()
        return redirect(f"/{index}/manga/{id_user}/")
    else:
        user.web_reading_mode_status = "on"
        db.session.commit()
        return redirect(f"/{index}/manga/{id_user}/")


@app.route("/mode/get-web-server/<id_user>/")
def get_web_server_mode(id_user):
    return jsonify(msg=web_server_mode_status(id_user)), 200


@app.route("/mode/r18", methods=["GET"])
def r18_mode_sever():
    mode = ServerMode.query.filter_by(mode_name="r18").first()
    status = mode.status
    index = session["server"]

    if status == "on":
        mode.status = "off"
    else:
        mode.status = "on"

    db.session.commit()
    return redirect(f"/{index}/manga/0/")


@app.route("/web/rmanga/<index>/<path>/")
@cross_origin(origin="*")
def get_manga_from_web(index, path):
    try:
        funct = list_api_from_server[f"{index}"][0]
        return funct(path)
    except Exception as e:
        print(e)
        return jsonify({"errMsg": "Internal Server Error"}, {"errCode": str(e)}), 500


@app.route("/web/rnovel/<index>/<path>/")
@cross_origin(origin="*")
def get_novel_from_web(index, path):
    try:
        funct = list_api_from_server[f"{index}"][0]
        return funct(path)
    except Exception as e:
        print(e)
        return jsonify({"errMsg": "Internal Server Error"}, {"errCode": str(e)}), 500


@app.route("/web/rmanga/<index>/<path>/<id_chapter>/")
@cross_origin(origin="*")
def get_image_chapter_from_web(index, path, id_chapter):
    try:
        funct = list_api_from_server[f"{index}"][1]
        return funct(path, id_chapter)
    except Exception as e:
        print(e)
        return jsonify({"errMsg": "Internal Server Error"}, {"errCode": str(e)}), 500


@app.route("/web/rnovel/<index>/<path>/<id_chapter>/")
@cross_origin(origin="*")
def get_content_chapter_from_web(index, path, id_chapter):
    try:
        funct = list_api_from_server[f"{index}"][1]
        return funct(path, id_chapter)
    except Exception as e:
        print(e)
        return jsonify({"errMsg": "Internal Server Error"}, {"errCode": str(e)}), 500


@app.route("/log_user/<id_user>", methods=["GET", "POST"])
def log_user(id_user):
    if request.method == "POST":
        data = request.json
        print("_______DATA____" + str(data))
        path_segment_manga = data["path_segment_manga"]
        path_segment_chapter = data["path_segment_chapter"]
        type = data["type"]
        index = data["index"]
        if id_user == 0:
            return jsonify({"message": "login to save history"})
        user = Users.query.filter(Users.id_user == id_user).first()
        if user:
            profile = Profiles.query.filter_by(id_user=id_user).first()
            if profile:
                profile.number_reads += 1
            log_user = LogUser.query.filter_by(
                path_segment_manga=path_segment_manga,
                path_segment_chapter=path_segment_chapter,
            ).first()
            manga = List_Manga.query.filter(
                List_Manga.path_segment_manga == path_segment_manga
            ).first()
            chapter = List_Chapter.query.filter(
                List_Chapter.path_segment_chapter == path_segment_chapter,
                List_Chapter.id_manga == manga.id_manga,
            ).first()
            time = datetime.now().strftime("%d/%m/%Y")
            if manga and chapter:
                if log_user is None:
                    data = LogUser(
                        id_user=id_user,
                        title_manga=manga.title_manga,
                        path_segment_manga=path_segment_manga,
                        title_chapter=chapter.title_chapter,
                        path_segment_chapter=path_segment_chapter,
                        poster=manga.poster_original,
                        type=type,
                        index=index,
                        read_time=time,
                    )
                    db.session.add(data)
                else:
                    log_user.read_time = time
            else:
                return jsonify({"message": "chapter not found"})
            db.session.commit()
            return jsonify({"message": "History is saved"})
        else:
            return jsonify({"message": "user not found"})
    if request.method == "GET":
        try:
            result = []
            list_manga = []
            localhost = split_join(request.url)
            log_user = (
                LogUser.query.filter(LogUser.id_user == id_user)
                .order_by(LogUser.id.desc())
                .all()
            )
            for item in log_user:
                title_manga = item.title_manga
                if title_manga in list_manga:
                    continue
                else:
                    list_manga.append(title_manga)

                server = List_Server.query.filter(
                    List_Server.index == item.index
                ).first()
                name_server = server.name_server.replace("https:", "").replace("/", "")

                link_manga = make_link(
                    localhost, f"/r{item.type}/{item.path_segment_manga}"
                )
                link_chapter = make_link(
                    localhost,
                    f"/r{item.type}/{item.path_segment_manga}/{item.path_segment_chapter}",
                )

                data = {
                    "title_manga": title_manga,
                    "link_manga": link_manga,
                    "title_chapter": item.title_chapter,
                    "link_chapter": link_chapter,
                    "poster": item.poster,
                    "type": item.type,
                    "index_server": item.index,
                    "name_server": name_server,
                    "readAt": item.read_time.strftime("%d/%m/%Y"),
                    # 'readAt': item.read_time.strftime("%a, %d %b %Y %H:%M:%S GMT"),
                }
                result.append(data)
            return result
        except Exception as e:
            print(e)
            return jsonify({"message": f"Erorr {e}"})
