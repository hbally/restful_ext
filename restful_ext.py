# -*- coding: utf-8 -*-
# @Time    : 2017/11/29 15:16
# @Author  : Ayan
# @Email   : hbally
# @Software: PyCharm

from flask import Flask

from flask import request
from flask import jsonify
import json
import pprint
import functools
import errors
import logging
import os

app = Flask(__name__)
#
current_dir = os.path.dirname(os.path.abspath(__file__))
handler = logging.FileHandler(current_dir + '/log.log', encoding='UTF-8')
handler.setLevel(logging.INFO)
logging_format = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)s - %(message)s')
handler.setFormatter(logging_format)
app.logger.addHandler(handler)
#
logger = app.logger


@app.route('/')
def hello_world():
    return 'Hello World!'


def mobile_request(func):
    """请求装饰器：封装请求的和响应：请求提取参数，并且同意处理常规异常;响应：自定义响应格式"""

    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        # put all parameters into kwargs
        kwargs = kwargs if kwargs else {'testkey': 'testvalue'}
        if request.args:  # get param
            kwargs.update(request.args.to_dict())
        if request.form:  # post param
            kwargs.update(request.form.to_dict())
        if request.data:  # request body
            kwargs.update(json.loads(request.data))
        # todo: request.files
        # if request.headers.get('Authorization'):
        #     encrypted_token = request.headers.get('Authorization')
        #     is_valid, user_id = logic_user.is_token_valid(encrypted_token)
        #     if not is_valid:
        #         # AuthTokenInvalid
        #         abort(401)
        #     user = logic_user.get_user_by_id(user_id)
        #     if not user:
        #         # token is valid, but maybe user is deleted.UserNotFound
        #         abort(401)
        #     kwargs["user_id"] = user_id
        try:
            log_mobile_request(func.__name__, args, kwargs)
            # 被装饰的函数处理中
            result = func(*args, **kwargs)
            response = {
                'rc': 0,
                'data': result
            }
        except Exception as e:  # 自定义异常处理
            logger.exception(e.message)  # logger will send email with this exception
            rc = getattr(e, 'rc', errors.UnknownError.rc)
            err_msg = getattr(e, 'msg', errors.UnknownError.msg)
            response = {
                'rc': rc,
                'msg': err_msg,
            }

        log_mobile_response(response)
        return jsonify(response)

    return wrapped


def log_mobile_response(response):
    """打印响应日志"""
    logger.info("""Return mobile response:
        response: %s""" % response)


def log_mobile_request(funcname, args, kwargs):
    """打印请求日志"""
    logger.info("""Handle mobile request:
        func: %s
        args: %s
        kwargs: %s""" % (funcname, pprint.pformat(args), pprint.pformat(kwargs)))


###########################POST请求示范start##############################################
@app.route("/diary", methods=['POST'])
@mobile_request  # 拨离请求，封装响应
def api_create_diary(**kwargs):
    """接口View层：处理http进出"""
    return logic_create_diary(kwargs['user_id'], kwargs['title'], kwargs['content'])

def logic_create_diary(user_id, title, content):
    """接口Business层：处理业务吹拉弹唱,必要时抛出异常供mobile_request捕获处理"""
    result = {}
    #处理前置逻辑
    result_pre = {}
    #处理数据库逻辑 result_db中包含数Model
    result_db = db_create_diary(user_id, title, content)
    #处理后置逻辑 转换result_db中model过渡到json
    result = {"msg": "----ok----"}
    logger.debug("userId :%s title :%s content :%s" % (user_id, title, content))
    return result

def db_create_diary(user_id, title, content):
    "接口Model层：直接接触数据库查询,提供数据Model ,必要时抛出异常供mobile_request捕获处理"
    return {}

###########################POST请求示范end##############################################

if __name__ == '__main__':
    app.run(debug=True)
