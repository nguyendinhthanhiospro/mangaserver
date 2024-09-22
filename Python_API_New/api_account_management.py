import json
from urllib.request import urlopen

from flask import redirect, request
from wtforms import SubmitField
from main import *
from datetime import datetime
from main.form import SwitchForm, RegisterForm

from main.model import LogUser, TrackingUser
import flask
import random
import mysql.connector
from email.message import EmailMessage

config = {
    "user": "sonpro",
    "password": "Ratiendi89",
    "host": "localhost",
    "port": 3306,
    "database": "FutureLove4",
    "auth_plugin": "mysql_native_password",
}


def get_data_email():
    try:
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        cursor.execute("SELECT gmail, password_app FROM gmail_from")
        gmail_data = cursor.fetchall()
        # Choose a random row from gmail_data
        data = random.choice(gmail_data)
        print(str(data))
    except mysql.connector.Error as error:
        print(f"Failed to connect to MySQL database: {error}")
    finally:
        if "connection" in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection closed")
    return data


async def send_mail_to_email(email, link, user_name, device_register):
    try:

        MainData_body = f""" 
            <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
            <html dir="ltr" xmlns="http://www.w3.org/1999/xhtml" xmlns:o="urn:schemas-microsoft-com:office:office">

            <head>
                <meta charset="UTF-8">
                <meta content="width=device-width, initial-scale=1" name="viewport">
                <meta name="x-apple-disable-message-reformatting">
                <meta http-equiv="X-UA-Compatible" content="IE=edge">
                <meta content="telephone=no" name="format-detection">
                <title></title>
                <!--[if (mso 16)]>
                <style type="text/css">
                
                </style>
                <![endif]-->
                
                <!--[if gte mso 9]>
            <xml>
                <o:OfficeDocumentSettings>
                <o:AllowPNG></o:AllowPNG>
                <o:PixelsPerInch>96</o:PixelsPerInch>
                </o:OfficeDocumentSettings>
            </xml>
            <![endif]-->
                <!--[if !mso]><!-- -->
                <link href="https://fonts.googleapis.com/css2?family=Imprima&display=swap" rel="stylesheet">
                <!--<![endif]-->
            </head>

            <body>
                <div dir="ltr" class="es-wrapper-color">
                    <!--[if gte mso 9]>
                        <v:background xmlns:v="urn:schemas-microsoft-com:vml" fill="t">
                            <v:fill type="tile" color="#ffffff"></v:fill>
                        </v:background>
                    <![endif]-->
                    <table class="es-wrapper" width="100%" cellspacing="0" cellpadding="0">
                        <tbody>
                            <tr>
                                <td class="esd-email-paddings" valign="top">
                                    <table cellpadding="0" cellspacing="0" class="es-footer esd-header-popover" align="center">
                                        <tbody>
                                            <tr>
                                                <td class="esd-stripe" align="center">
                                                    <table bgcolor="#bcb8b1" class="es-footer-body" align="center" cellpadding="0" cellspacing="0" width="600">
                                                        <tbody>
                                                            <tr>
                                                                <td class="esd-structure es-p20t es-p20b es-p40r es-p40l" align="left">
                                                                    <table cellpadding="0" cellspacing="0" width="100%">
                                                                        <tbody>
                                                                            <tr>
                                                                                <td width="520" class="esd-container-frame" align="center" valign="top">
                                                                                    <table cellpadding="0" cellspacing="0" width="100%">
                                                                                        <tbody>
                                                                                            <tr>
                                                                                                <td align="center" class="esd-empty-container" style="display: none;"></td>
                                                                                            </tr>
                                                                                        </tbody>
                                                                                    </table>
                                                                                </td>
                                                                            </tr>
                                                                        </tbody>
                                                                    </table>
                                                                </td>
                                                            </tr>
                                                        </tbody>
                                                    </table>
                                                </td>
                                            </tr>
                                        </tbody>
                                    </table>
                                    <table cellpadding="0" cellspacing="0" class="es-content" align="center">
                                        <tbody>
                                            <tr>
                                                <td class="esd-stripe" align="center">
                                                    <table bgcolor="#efefef" class="es-content-body" align="center" cellpadding="0" cellspacing="0" width="600" style="border-radius: 20px 20px 0 0 ">
                                                        <tbody>
                                                            <tr>
                                                                <td class="esd-structure es-p40t es-p40r es-p40l" align="left">
                                                                    <table cellpadding="0" cellspacing="0" width="100%">
                                                                        <tbody>
                                                                            <tr>
                                                                                <td width="520" class="esd-container-frame" align="center" valign="top">
                                                                                    <table cellpadding="0" cellspacing="0" width="100%">
                                                                                        <tbody>

                                                                                        </tbody>
                                                                                    </table>
                                                                                </td>
                                                                            </tr>
                                                                        </tbody>
                                                                    </table>
                                                                </td>
                                                            </tr>
                                                            <tr>
                                                                <td class="es-p20t es-p40r es-p40l esd-structure" align="left">
                                                                    <table cellpadding="0" cellspacing="0" width="100%">
                                                                        <tbody>
                                                                            <tr>
                                                                                <td width="520" class="esd-container-frame" align="center" valign="top">
                                                                                    <table cellpadding="0" cellspacing="0" width="100%" bgcolor="#fafafa" style="background-color: #fafafa; border-radius: 10px; border-collapse: separate;">
                                                                                        <tbody>
                                                                                            <tr>
                                                                                                <td align="left" class="esd-block-text es-p20">
                                                                                                    <h3>Welcome, {user_name}</h3>
                                                                                                    <p><br></p>
                                                                                                    <p>You recently requested to open your MangaSocial account. Use the button below to confirmation.<br><br>Confirm your email address by clicking the button below. This step adds extra security to your business by verifying you own this email.</p>
                                                                                                </td>
                                                                                            </tr>
                                                                                        </tbody>
                                                                                    </table>
                                                                                </td>
                                                                            </tr>
                                                                        </tbody>
                                                                    </table>
                                                                </td>
                                                            </tr>
                                                        </tbody>
                                                    </table>
                                                </td>
                                            </tr>
                                        </tbody>
                                    </table>
                                    <table cellpadding="0" cellspacing="0" class="es-content" align="center">
                                        <tbody>
                                            <tr>
                                                <td class="esd-stripe" align="center">
                                                    <table bgcolor="#efefef" class="es-content-body" align="center" cellpadding="0" cellspacing="0" width="600">
                                                        <tbody>
                                                            <tr>
                                                                <td class="esd-structure es-p30t es-p40b es-p40r es-p40l" align="left">
                                                                    <table cellpadding="0" cellspacing="0" width="100%">
                                                                        <tbody>
                                                                            <tr>
                                                                                <td width="520" class="esd-container-frame" align="center" valign="top">
                                                                                    <table cellpadding="0" cellspacing="0" width="100%">
                                                                                        <tbody>
                                                                                            <tr>
                                                                                                <td align="center" class="esd-block-button">
                                                                                                    <!--[if mso]><a href="" target="_blank" hidden>
                <v:roundrect xmlns:v="urn:schemas-microsoft-com:vml" xmlns:w="urn:schemas-microsoft-com:office:word" esdevVmlButton href="{link}" 
                            style="height:56px; v-text-anchor:middle; width:520px" arcsize="50%" stroke="f"  fillcolor="#fff">
                    <w:anchorlock></w:anchorlock>
                    <center style='color:#ffffff; font-family:Imprima, Arial, sans-serif; font-size:22px; font-weight:700; line-height:22px;  mso-text-raise:1px'>Confirm email</center>
                </v:roundrect></a>
            <![endif]-->
                                                                                                    <!--[if !mso]><!-- --><span class="msohide es-button-border" style="display: block; background: #fff;"><a href="{link}" class="es-button msohide" target="_blank" style="padding-left: 5px; padding-right: 5px; display: block; background: #fff; mso-border-alt: 10px solid  #fff">Confirm email</a></span>
                                                                                                    <!--<![endif]-->
                                                                                                </td>
                                                                                            </tr>
                                                                                        </tbody>
                                                                                    </table>
                                                                                </td>
                                                                            </tr>
                                                                        </tbody>
                                                                    </table>
                                                                </td>
                                                            </tr>
                                                            <tr>
                                                                <td class="esd-structure es-p40r es-p40l" align="left">
                                                                    <table cellpadding="0" cellspacing="0" width="100%">
                                                                        <tbody>
                                                                            <tr>
                                                                                <td width="520" class="esd-container-frame" align="center" valign="top">
                                                                                    <table cellpadding="0" cellspacing="0" width="100%">
                                                                                        <tbody>
                                                                                            <tr>
                                                                                                <td align="left" class="esd-block-text">
                                                                                                    <p>Thanks,<br><br>MangaSocial Team!</p>
                                                                                                </td>
                                                                                            </tr>
                                                                                            <tr>
                                                                                                <td align="center" class="esd-block-spacer es-p40t es-p20b" style="font-size:0">
                                                                                                    <table border="0" width="100%" height="100%" cellpadding="0" cellspacing="0">
                                                                                                        <tbody>
                                                                                                            <tr>
                                                                                                                <td style="border-bottom: 1px solid #666666; background: unset; height: 1px; width: 100%; margin: 0px;"></td>
                                                                                                            </tr>
                                                                                                        </tbody>
                                                                                                    </table>
                                                                                                </td>
                                                                                            </tr>
                                                                                        </tbody>
                                                                                    </table>
                                                                                </td>
                                                                            </tr>
                                                                        </tbody>
                                                                    </table>
                                                                </td>
                                                            </tr>
                                                        </tbody>
                                                    </table>
                                                </td>
                                            </tr>
                                        </tbody>
                                    </table>
                                    <table cellpadding="0" cellspacing="0" class="es-content" align="center">
                                        <tbody>
                                            <tr>
                                                <td class="esd-stripe" align="center">
                                                    <table bgcolor="#efefef" class="es-content-body" align="center" cellpadding="0" cellspacing="0" width="600" style="border-radius: 0 0 20px 20px">
                                                        <tbody>
                                                            <tr>
                                                                <td class="esd-structure es-p20t es-p20b es-p40r es-p40l esdev-adapt-off" align="left">
                                                                    <table width="520" cellpadding="0" cellspacing="0" class="esdev-mso-table">
                                                                        <tbody>
                                                                            <tr>
                                                                                <td class="esdev-mso-td" valign="top">
                                                                                    <table cellpadding="0" cellspacing="0" align="left" class="es-left">
                                                                                        <tbody>
                                                                                            <tr>
                                                                                                <td width="47" class="esd-container-frame" align="center" valign="top">
                                                                                                    <table cellpadding="0" cellspacing="0" width="100%">
                                                                                                        <tbody>
                                                                                                            <tr>
                                                                                                                <td align="center" class="esd-block-image es-m-txt-l" style="font-size: 0px;"><a target="_blank" href="https://ibb.co/c3Tqtm0"><img src="https://i.ibb.co/h980Hqb/love.png" alt="Demo" style="display: block;" width="47" title="Demo"></a></td>
                                                                                                            </tr>
                                                                                                        </tbody>
                                                                                                    </table>
                                                                                                </td>
                                                                                            </tr>
                                                                                        </tbody>
                                                                                    </table>
                                                                                </td>
                                                                                <td width="20"></td>
                                                                                <td class="esdev-mso-td" valign="top">
                                                                                    <table cellpadding="0" cellspacing="0" class="es-right" align="right">
                                                                                        <tbody>
                                                                                            <tr>
                                                                                                <td width="453" class="esd-container-frame" align="center" valign="top">
                                                                                                    <table cellpadding="0" cellspacing="0" width="100%">
                                                                                                        <tbody>
                                                                                                            <tr>
                                                                                                                <td align="left" class="esd-block-text">
                                                                                                                    <p style="font-size: 16px;">This link expire in 24 hours. If you have questions, <a target="_blank" style="font-size: 16px;" href="https://viewstripo.email">we're here to help</a></p>
                                                                                                                </td>
                                                                                                            </tr>
                                                                                                        </tbody>
                                                                                                    </table>
                                                                                                </td>
                                                                                            </tr>
                                                                                        </tbody>
                                                                                    </table>
                                                                                </td>
                                                                            </tr>
                                                                        </tbody>
                                                                    </table>
                                                                </td>
                                                            </tr>
                                                        </tbody>
                                                    </table>
                                                </td>
                                            </tr>
                                        </tbody>
                                    </table>
                                    <table cellpadding="0" cellspacing="0" class="es-footer" align="center">
                                        <tbody>
                                            <tr>
                                                <td class="esd-stripe" align="center">
                                                    <table bgcolor="#bcb8b1" class="es-footer-body" align="center" cellpadding="0" cellspacing="0" width="600">
                                                        <tbody>
                                                            <tr>
                                                                <td class="esd-structure es-p40t es-p30b es-p20r es-p20l" align="left" esd-custom-block-id="853188">
                                                                    <table cellpadding="0" cellspacing="0" width="100%">
                                                                        <tbody>
                                                                            <tr>
                                                                                <td width="560" align="left" class="esd-container-frame">
                                                                                    <table cellpadding="0" cellspacing="0" width="100%">
                                                                                        <tbody>
                                                                                            <tr>
                                                                                                <td align="center" class="esd-block-image es-p20b es-m-txt-c" style="font-size: 0px;"><a target="_blank"><img src="https://i.ibb.co/h980Hqb/love.png" alt="Logo" style="display: block; font-size: 12px;" title="Logo" height="60"></a></td>
                                                                                            </tr>
                                                                                            <tr>
                                                                                                <td align="center" class="esd-block-social es-m-txt-c es-p10t es-p20b" style="font-size:0">
                                                                                                    <table cellpadding="0" cellspacing="0" class="es-table-not-adapt es-social">
                                                                                                        <tbody>
                                                                                                            <tr>
                                                                                                                <td align="center" valign="top" esd-tmp-icon-type="twitter" class="es-p5r"><a target="_blank" href><img src="https://tlr.stripocdn.email/content/assets/img/social-icons/logo-black/twitter-logo-black.png" alt="Tw" title="Twitter" height="24"></a></td>
                                                                                                                <td align="center" valign="top" esd-tmp-icon-type="facebook" class="es-p5r"><a target="_blank" href><img src="https://tlr.stripocdn.email/content/assets/img/social-icons/logo-black/facebook-logo-black.png" alt="Fb" title="Facebook" height="24"></a></td>
                                                                                                                <td align="center" valign="top" esd-tmp-icon-type="linkedin"><a target="_blank" href><img src="https://tlr.stripocdn.email/content/assets/img/social-icons/logo-black/linkedin-logo-black.png" alt="In" title="Linkedin" height="24"></a></td>
                                                                                                            </tr>
                                                                                                        </tbody>
                                                                                                    </table>
                                                                                                </td>
                                                                                            </tr>
                                                                                            <tr>
                                                                                                <td align="center" class="esd-block-text" esd-links-underline="none">
                                                                                                    <p style="font-size: 13px;"><a target="_blank" style="text-decoration: none;"></a><a target="_blank" style="text-decoration: none;">Privacy Policy</a><a target="_blank" style="font-size: 13px; text-decoration: none;"></a> • <a target="_blank" style="text-decoration: none;">Unsubscribe</a></p>
                                                                                                </td>
                                                                                            </tr>
                                                                                            <tr>
                                                                                                <td align="center" class="esd-block-text es-p20t" esd-links-underline="none">
                                                                                                    <p><a target="_blank"></a>Copyright © 2023 ThinkDiff Company<a target="_blank"></a></p>
                                                                                                </td>
                                                                                            </tr>
                                                                                        </tbody>
                                                                                    </table>
                                                                                </td>
                                                                            </tr>
                                                                        </tbody>
                                                                    </table>
                                                                </td>
                                                            </tr>
                                                        </tbody>
                                                    </table>
                                                </td>
                                            </tr>
                                        </tbody>
                                    </table>
                                    <table cellpadding="0" cellspacing="0" class="es-footer esd-footer-popover" align="center">
                                        <tbody>
                                            <tr>
                                                <td class="esd-stripe" align="center" esd-custom-block-id="819294">
                                                    <table bgcolor="#ffffff" class="es-footer-body" align="center" cellpadding="0" cellspacing="0" width="600">
                                                        <tbody>
                                                            <tr>
                                                                <td class="esd-structure es-p20" align="left">
                                                                    <table cellpadding="0" cellspacing="0" width="100%">
                                                                        <tbody>
                                                                            <tr>
                                                                                <td width="560" class="esd-container-frame" align="left">
                                                                                    <table cellpadding="0" cellspacing="0" width="100%">
                                                                                        <tbody>
                                                                                            <tr>
                                                                                                <td align="center" class="esd-empty-container" style="display: none;"></td>
                                                                                            </tr>
                                                                                        </tbody>
                                                                                    </table>
                                                                                </td>
                                                                            </tr>
                                                                        </tbody>
                                                                    </table>
                                                                </td>
                                                            </tr>
                                                        </tbody>
                                                    </table>
                                                </td>
                                            </tr>
                                        </tbody>
                                    </table>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </body>

            </html>
"""
        print("_____truoc_khi_guimail_____")
        data = get_data_email()
        print(data[0], [data[1]])

        msg = EmailMessage()
        msg["Subject"] = "Verify Account MangaSocial.online"
        msg["From"] = "devmobilepro1888@gmail.com"
        msg["To"] = email
        msg.set_content(
            f"""\
            {MainData_body} + {user_name}
        """,
            subtype="html",
        )
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.ehlo()
        server.login(data[0], data[1])
        server.send_message(msg)

        server.close()
    except Exception as e:
        print("An error occurred while sending the email:")
        print(str(e))
        print(email, link, user_name, device_register)
        return str(e)


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(user_id)


@app.route("/register", methods=["POST"])
async def register_handle_post():
    try:
        form = RegisterForm()
        print(
            "_______________________________________register_handle_post vao phan dang ky tai khoan_____"
        )
        print(form.email.data)
        # if form.validate_on_submit():
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
            # thr = Thread(target=send_email, args=[msg])
            # thr.start()

            email_user = form.email.data
            password_hash = generate_password_hash(form.password.data)
            time = datetime.now().strftime("%H:%M:%S %d-%m-%Y")
            user = Users(email=email_user, password=password_hash, time_register=time)
            db.session.add(user)
            db.session.commit()
            find_user = Users.query.filter_by(email=form.email.data).first()
            profile = Profiles(
                id_user=find_user.id_user,
                name_user=find_user.email,
                participation_time=convert_time(user.time_register),
            )
            db.session.add(profile)
            db.session.commit()
            await send_mail_to_email(
                form.email.data, confirm_url, data, form.password.data
            )  # send email by email
            return (
                jsonify(
                    message="Register Account Done",
                    account={"email": form.email.data},
                ),
                200,
            )
        # else:
        #     return (
        #         jsonify(
        #             message="Please input more data",
        #             account={"email": form.email.data},
        #         ),
        #         200,
        #     )
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

                    ip_login = ""
                    location_ip = ""
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


@app.route("/<string:id>/setting/password", methods=["PATCH", "POST"])
# @login_required
async def user_setting_password(id):
    form = SettingPasswordForm()
    if form.validate_on_submit():
        current_password = form.current_password.data
        new_password = form.new_password.data
        confirm_password = form.confirm_password.data

        # id_user = current_user.id_user
        # id_user = id
        account = Users.query.get_or_404(id)

        is_password_correct = check_password_hash(account.password, current_password)
        if not is_password_correct:
            return jsonify(message="Incorrect current password"), 400
        else:
            # data = {
            #     "current_password": current_password,
            #     "new_password": new_password,
            #     "confirm_password": confirm_password,
            #     "id_user": account.id_user,
            # }
            hashed_password = generate_password_hash(new_password)
            account.password = hashed_password
            db.session.commit()
            # json_data = json.dumps(data, ensure_ascii=False)
            # token = secret.dumps(json_data, salt=app.config["SECURITY_PASSWORD_SALT"])
            # msg = Message(
            #     "Confirmation",
            #     sender=app.config["MAIL_USERNAME"],
            #     recipients=[account.email],
            # )
            # confirm_url = url_for(
            #     "setting_password_confirm", token=token, _external=True
            # )
            # msg.body = "Your confirmation link is " + confirm_url
            # thr = Thread(target=send_email, args=[msg])
            # thr.start()
            # link = url_for("setting_password_confirm", token=token, _external=True)

            # await send_mail_to_email(account.email, link, new_password, account.email)

            return (
                jsonify(
                    message="Change Password Successful",
                ),
                200,
            )
    return jsonify(errors=form.errors), 400


@app.route("/setting/password/confirm/<token>")
def setting_password_confirm(token):
    try:
        confirmed = secret.loads(
            token, salt=app.config["SECURITY_PASSWORD_SALT"], max_age=600
        )
    except Exception:
        return {"message": "Your link was expired. Try again"}
    confirmed_email = json.loads(confirmed)
    hashed_password = generate_password_hash(confirmed_email["new_password"])
    account = Users.query.filter_by(id_user=confirmed_email["id_user"]).first()
    account.password = hashed_password
    logout_user()
    db.session.commit()

    return {"message": "Confirm successfully. Try to login"}


@app.route("/forgot-password", methods=["PATCH", "POST"])
async def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        email = form.email.data
        new_password = form.new_password.data
        confirm_password = form.confirm_password.data
        try:
            account = Users.query.filter_by(email=email).first()
            data = {
                "email": email,
                "new_password": new_password,
                "confirm_password": confirm_password,
                "id_user": account.id_user,
            }
            # token = secret.dumps(data, salt=app.config["SECURITY_PASSWORD_SALT"])
            # msg = Message(
            #     "Confirmation",
            #     sender=app.config["MAIL_USERNAME"],
            #     recipients=[account.email],
            # )
            # confirm_url = url_for(
            #     "forgot_password_confirm", token=token, _external=True
            # )
            # msg.body = "Your confirmation link is " + confirm_url
            # thr = Thread(target=send_email, args=[msg])
            # thr.start()
            json_data = json.dumps(data, ensure_ascii=False)
            token = secret.dumps(json_data, salt=app.config["SECURITY_PASSWORD_SALT"])
            link = url_for("forgot_password_confirm", token=token, _external=True)

            await send_mail_to_email(
                account.email, link, new_password, account.email
            )  # send email by email

            return (
                jsonify(
                    message="Please check your email or spam",
                    account={"email": account.email},
                ),
                200,
            )
        except Exception as e:
            return jsonify(message="Account does not exist"), 404
    return jsonify(error=form.errors), 400


@app.route("/forgot-password/confirm/<token>")
def forgot_password_confirm(token):
    try:
        confirmed = secret.loads(
            token, salt=app.config["SECURITY_PASSWORD_SALT"], max_age=600
        )
    except Exception:
        return {"message": "Your link was expired. Try again"}
    confirmed_email = json.loads(confirmed)
    print(confirmed_email)
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
            image_url = split_join(request.url) + f"/image/avatar/{pic_name}/"
            profile_user.avatar_user = image_url

            data = {"Avatar user": image_url}
            result.append(data)

        if result:
            db.session.commit()
            return jsonify(message="User Updated Successfully!", data=result)
        else:
            return jsonify(message="No information updated")

    return jsonify(Error=form.errors), 400


@app.route("/image/avatar/<file_name>/")
def get_file(file_name):
    try:
        return send_from_directory(app.config["UPLOAD_FOLDER"], file_name)
    except FileNotFoundError:
        jsonify(Error=form.errors), 404


@app.route("/image/logo/<file_name>/")
def get_file_logo(file_name):
    try:
        return send_from_directory(
            "/home/thinkdiff/Documents/manganelon/mangareader/Python_API_New/image/",
            file_name,
        )
    except FileNotFoundError:
        jsonify(Error=form.errors), 404


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


@app.route("/user/location-information/", methods=["GET"])
def get_location_information():
    ip_address = get_ip()
    ip_location = DbIpCity.get(ip_address=ip_address, api_key="free")
    data = {
        "ip_address": ip_address,
        "country": ip_location.country,
        "city": ip_location.city,
        "region": ip_location.region,
        "latitude": ip_location.latitude,
        "longitude": ip_location.longitude,
    }
    return data
