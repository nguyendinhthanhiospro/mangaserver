import json
from urllib.request import urlopen

from flask import redirect, request
from wtforms import SubmitField
from main import *
from datetime import datetime
from main.form import SwitchForm, RegisterForm

from main.model import LogUser, TrackingUser
import flask


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(user_id)


@app.route("/register", methods=["POST"])
def register_handle_post():
    try:
        form = RegisterForm()
        print("posted")
        if form.validate_on_submit():
            print("validated")
            account = Users.query.filter_by(email=form.email.data).first()
            if account:
                return jsonify(message="Account already exists!"), 400
            else:
                data = {"email": form.email.data, "password": form.password.data}
                token = secret.dumps(data, salt=app.config["SECURITY_PASSWORD_SALT"])
                confirm_url = url_for("register_confirm", token=token, _external=True)
                msg = Message(
                    "Confirmation",
                    sender=app.config["MAIL_USERNAME"],
                    recipients=[form.email.data],
                )
                msg.body = "Your confirmation link is " + confirm_url
                thr = Thread(target=send_email, args=[msg])
                thr.start()
                return (
                    jsonify(
                        message="Please check your email or spam",
                        account={"email": form.email.data},
                    ),
                    200,
                )
    except Exception as e:
        return {"errMsg": "Something went wrong!", "errCode": str(e)}, 500


@app.route("/register", methods=["GET"])
def register_handle_get():
    form = RegisterForm()
    return jsonify(errors=form.errors)


@app.route("/register/confirm/<token>")
def register_confirm(token):
    try:
        try:
            confirmed_email = secret.loads(
                token, salt=app.config["SECURITY_PASSWORD_SALT"]
            )
        except Exception:
            return {"message": "Your link was expired. Try again"}

        account = Users.query.filter_by(email=confirmed_email["email"]).first()
        if account:
            return jsonify(message="Your account was already confirm")
        else:
            email_user = confirmed_email["email"]
            password_hash = generate_password_hash(confirmed_email["password"])
            time = datetime.now().strftime("%H:%M:%S %d-%m-%Y")
            user = Users(email=email_user, password=password_hash, time_register=time)
            db.session.add(user)
            db.session.commit()
            find_user = Users.query.filter_by(email=confirmed_email["email"]).first()
            profile = Profiles(
                id_user=find_user.id_user,
                name_user=find_user.email,
                participation_time=convert_time(user.time_register),
            )
            db.session.add(profile)
            db.session.commit()
        return {"message": "Confirm successfully. Try to login"}
    except Exception as e:
        return {"errMsg": "Something went wrong!", "errCode": str(e)}, 500


@app.route("/login", methods=["GET", "POST"])
def login():
    try:
        form = LoginForm()
        if form.validate_on_submit():
            account = Users.query.filter_by(email=form.email.data).first()
            # print('ID User: ', account.id_user)
            if account:
                print("Password checking ...")
                is_pass_correct = check_password_hash(
                    account.password, form.password.data
                )
                if is_pass_correct:
                    print("Password correct")
                    login_user(account)

                    # luu thoi gian, ip, location dang nhap
                    id_user = current_user.id_user
                    time = datetime.now().strftime("%H:%M:%S %d-%m-%Y")
                    tracking = TrackingUser.query.filter_by(id_user=id_user).first()

                    try:
                        ip_login = f"{get_ip()}"
                        location_ip = f"{get_location()}"
                    except:
                        pass

                    if tracking is None:
                        data = TrackingUser(
                            id_user=id_user,
                            login_time=time,
                            login_last_time=None,
                            logout_time=None,
                            status="online",
                            ip_login=ip_login,
                            location_login=location_ip,
                        )
                        db.session.add(data)
                    else:
                        tracking.login_last_time = tracking.login_time
                        tracking.login_time = time
                        tracking.status = "online"
                        tracking.ip_login = ip_login
                        tracking.location_login = location_ip
                    db.session.commit()

                    return (
                        jsonify(
                            errCode=200,
                            message="Login successfully",
                            account={
                                "id_user": account.id_user,
                                "email": account.email,
                                "password": account.password,
                            },
                        ),
                        200,
                    )
                else:
                    return jsonify(errCode=401, message="Incorrect password!")
            else:
                return jsonify(errCode=404, message="Account does not exist!")
    except Exception as e:
        return (
            jsonify(
                errCode=500,
                message="Something went wrong!",
            ),
            500,
        )


@app.route("/logout")
@login_required
def logout():
    try:
        id_user = current_user.id_user

        logout_user()
        # luu thoi gian dang nhap
        time = datetime.now().strftime("%H:%M:%S %d-%m-%Y")
        tracking = TrackingUser.query.filter_by(id_user=id_user).first()
        tracking.logout_time = time
        tracking.status = "offline"
        db.session.commit()

        return jsonify(message=f"Sign out successful!"), 200
    except Exception as e:
        return {"errMsg": "Something went wrong!", "errCode": str(e)}, 500


@app.route("/user/setting/password", methods=["PATCH", "POST"])
@login_required
def user_setting_password():
    form = SettingPasswordForm()
    if form.validate_on_submit():
        current_password = form.current_password.data
        new_password = form.new_password.data
        confirm_password = form.confirm_password.data

        id_user = current_user.id_user
        account = Users.query.get_or_404(id_user)

        is_password_correct = check_password_hash(account.password, current_password)
        if not is_password_correct:
            return jsonify(message="Incorrect current password"), 400
        else:
            data = {
                "current_password": current_password,
                "new_password": new_password,
                "confirm_password": confirm_password,
                "id_user": account.id_user,
            }
            token = secret.dumps(data, salt=app.config["SECURITY_PASSWORD_SALT"])
            msg = Message(
                "Confirmation",
                sender=app.config["MAIL_USERNAME"],
                recipients=[account.email],
            )
            confirm_url = url_for(
                "setting_password_confirm", token=token, _external=True
            )
            msg.body = "Your confirmation link is " + confirm_url
            thr = Thread(target=send_email, args=[msg])
            thr.start()
            return (
                jsonify(
                    message="Please check your email or spam",
                    account={"email": account.email},
                ),
                200,
            )
    return jsonify(errors=form.errors), 400


@app.route("/setting/password/confirm/<token>")
def setting_password_confirm(token):
    try:
        confirmed_email = secret.loads(
            token, salt=app.config["SECURITY_PASSWORD_SALT"], max_age=600
        )
    except Exception:
        return {"message": "Your link was expired. Try again"}
    hashed_password = generate_password_hash(confirmed_email["new_password"])
    account = Users.query.filter_by(id_user=confirmed_email["id_user"]).first()
    account.password = hashed_password
    logout_user()
    db.session.commit()

    return {"message": "Confirm successfully. Try to login"}


@app.route("/forgot-password", methods=["PATCH", "POST"])
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        email = form.email.data
        new_password = form.new_password.data
        confirm_password = form.confirm_password.data

        account = Users.query.filter_by(email=email).first()
        if account:
            data = {
                "email": email,
                "new_password": new_password,
                "confirm_password": confirm_password,
                "id_user": account.id_user,
            }
            token = secret.dumps(data, salt=app.config["SECURITY_PASSWORD_SALT"])
            msg = Message(
                "Confirmation",
                sender=app.config["MAIL_USERNAME"],
                recipients=[account.email],
            )
            confirm_url = url_for(
                "forgot_password_confirm", token=token, _external=True
            )
            msg.body = "Your confirmation link is " + confirm_url
            thr = Thread(target=send_email, args=[msg])
            thr.start()
            return (
                jsonify(
                    message="Please check your email or spam",
                    account={"email": account.email},
                ),
                200,
            )
        else:
            return jsonify(message="Account does not exist"), 404
    return jsonify(error=form.errors), 400


@app.route("/forgot-password/confirm/<token>")
def forgot_password_confirm(token):
    try:
        confirmed_email = secret.loads(
            token, salt=app.config["SECURITY_PASSWORD_SALT"], max_age=600
        )
    except Exception:
        return {"message": "Your link was expired. Try again"}
    hashed_password = generate_password_hash(confirmed_email["new_password"])
    account = Users.query.filter_by(id_user=confirmed_email["id_user"]).first()
    account.password = hashed_password
    db.session.commit()
    return {"message": "Confirm successfully. Try to login"}


@app.route("/user/<id_user>")
def user(id_user):
    account = Users.query.filter_by(id_user=id_user).first()
    profile = Profiles.query.filter_by(id_user=id_user).first()
    if profile and account:
        result = {
            "name_user": profile.name_user,
            "avatar_user": profile.avatar_user,
            "participation_time": convert_time(account.time_register),
            "number_reads": profile.number_reads,
            "number_comments": profile.number_comments,
            "date_of_birth": profile.date_of_birth,
            "gender": profile.gender,
            "introduction": profile.introduction,
            "job": profile.job,
        }
        return jsonify(result)
    else:
        return jsonify(message="User does not exist"), 404


@app.route("/user/setting/<id_user>/", methods=["PATCH", "POST"])
def user_setting(id_user):
    form = UserSettingForm()
    id_user = id_user
    profile_user = Profiles.query.get_or_404(id_user)

    if form.validate_on_submit():
        result = []
        if form.name_user.data:
            profile_user.name_user = form.name_user.data
            data = {"Name User": profile_user.name_user}
            result.append(data)

        if form.date_of_birth.data:
            profile_user.date_of_birth = form.date_of_birth.data.strftime("%d/%m/%Y")
            data = {"Date of birth": profile_user.date_of_birth}
            result.append(data)

        if form.gender.data:
            profile_user.gender = form.gender.data
            data = {"Gender": profile_user.gender}
            result.append(data)

        if form.introduction.data:
            profile_user.introduction = form.introduction.data
            data = {"Introduction": profile_user.introduction}
            result.append(data)

        if form.job.data:
            profile_user.job = form.job.data
            data = {"Job": profile_user.job}
            result.append(data)

        if form.avatar_user.data:
            avatar_file = form.avatar_user.data
            pic_filename = secure_filename(avatar_file.filename)
            formatted = datetime.now().strftime("%H%M%S%f-%d%m%Y")
            pic_name = f"{formatted}-{pic_filename}"
            saver = form.avatar_user.data
            saver.save(os.path.join(app.config["UPLOAD_FOLDER"], pic_name))
            imgbb = f"{path_folder_images}{pic_name}"

            data = {"Avatar user": imgbb}
            result.append(data)

        if result:
            db.session.commit()
            return jsonify(message="User Updated Successfully!", data=result)
        else:
            return jsonify(message="No information updated")

    return jsonify(Error=form.errors), 400


@app.route("/user/<id_user>/", methods=["DELETE"])
@login_required
def delete_user(id_user):
    user = Users.query.get_or_404(id_user)

    if user.id_user != current_user.id_user:
        return jsonify(error="You do not have permission to delete account"), 400

    comments = Comments.query.filter_by(id_user=id_user).all()

    for comment in comments:
        LikesComment.query.filter_by(id_comment=comment.id_comment).delete()
        delete_reply_comment(comment)
        db.session.delete(comment)
        CommentDiary.query.filter_by(id_comment=comment.id_comment).delete()

    LogUser.query.filter_by(id_user=id_user).delete()
    TrackingUser.query.filter_by(id_user=id_user).delete()
    Profiles.query.filter_by(id_user=id_user).delete()
    Users.query.filter_by(id_user=id_user).delete()

    db.session.commit()
    return jsonify(message="User deleted successfully")


@app.route("/user/log-user")
@login_required
def get_log_user():
    id_user = current_user.id_user
    result = []

    log_user = LogUser.query.filter(id_user == id_user).all()
    for manga in log_user:
        localhost = split_join(request.url)
        data = {
            "url_manga": make_link(localhost, f"/manga/{manga.path_segment_manga}/"),
            "title_manga": manga.title_manga,
            "categories": manga.categories,
            "poster": manga.poster,
            "rate": manga.rate,
            "url_chapter": make_link(
                localhost,
                f"/manga/{manga.path_segment_manga}/{manga.path_segment_chapter}",
            ),
        }
        result.append(data)

    return result


@app.route("/user/tracking-user")
@login_required
def get_tracking_user():
    id_user = current_user.id_user
    tracking = TrackingUser.query.filter_by(id_user=id_user).first()

    then = datetime.strptime(tracking.login_last_time, "%H:%M:%S %d-%m-%Y")
    now = datetime.now()

    time = get_time_diff(then, now)

    result = {
        "login_time": tracking.login_time,
        "logout_time": tracking.logout_time,
        "last_login_time": time,
    }

    return result


@app.route("/user/tracking-all-users")
def get_all_tracking_user():

    all_user = []
    tracking = TrackingUser.query.all()

    for user in tracking:
        if user.status == "online":
            time = get_time_diff(
                datetime.strptime(user.login_time, "%H:%M:%S %d-%m-%Y"), datetime.now()
            )
            data = {
                "id_user": user.id_user,
                "status": user.status,
                "login_time": user.login_time,
                "online_time": time,
                "ip_login": user.ip_login,
                "location_login": user.location_login,
            }

        else:
            time = get_time_diff(
                datetime.strptime(user.login_time, "%H:%M:%S %d-%m-%Y"),
                datetime.strptime(user.logout_time, "%H:%M:%S %d-%m-%Y"),
            )
            data = {
                "id_user": user.id_user,
                "status": user.status,
                "last_login_time": user.login_time,
                "last_logout_time": user.logout_time,
                "online_duration": time,
                "ip_login": user.ip_login,
                "location_ip": user.location_login,
            }

        all_user.append(data)

    return all_user


@app.route("/mode/r18/", methods=["GET", "POST"])
def switch():
    form = SwitchForm()

    if form.validate_on_submit():
        if form.state.label.text == "OFF":
            SwitchForm.state = SubmitField("ON")
        elif form.state.label.text == "ON":
            SwitchForm.state = SubmitField("OFF")

    if session.get("r18") == True:
        session["r18"] = False
    else:
        session["r18"] = True

    print(session.get("r18"))
    # return redirect(f'/{session.get("sever")}/')
    return redirect(url_for("get_home", index=session.get("sever")))


@app.route("/mode/r18_mode_status/", methods=["GET"])
def get_r18_mode_status():
    if r18_mode_status():
        status = "ON"
    else:
        status = "OFF"
    return jsonify({"status": status})
