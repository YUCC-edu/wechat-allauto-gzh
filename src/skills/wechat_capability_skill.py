import requests
import json
from typing import Dict, List, Optional, Any

class WeChatCapabilityManager:
    """微信公众号能力管理 API 客户端"""
    
    def __init__(self, app_id: str, app_secret: str):
        self.app_id = app_id
        self.app_secret = app_secret
        self.access_token = None
        
    def get_access_token(self) -> str:
        """获取 access_token"""
        url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={self.app_id}&secret={self.app_secret}"
        response = requests.get(url).json()
        if "access_token" in response:
            self.access_token = response["access_token"]
            return self.access_token
        raise Exception(f"获取 access_token 失败: {response}")

    def _request(self, method: str, endpoint: str, data: dict = None, params: dict = None) -> dict:
        """通用请求方法"""
        if not self.access_token:
            self.get_access_token()
            
        url = f"https://api.weixin.qq.com{endpoint}"
        if params is None:
            params = {}
        params['access_token'] = self.access_token
        
        if method.upper() == 'GET':
            response = requests.get(url, params=params)
        else:
            # 微信 API 通常要求 ensure_ascii=False 以避免中文乱码
            payload = json.dumps(data, ensure_ascii=False).encode('utf-8') if data else None
            response = requests.post(url, params=params, data=payload, headers={'Content-Type': 'application/json'})
            
        result = response.json()
        # 简单的 token 过期重试逻辑
        if result.get('errcode') in [40001, 40014, 42001]:
            self.get_access_token()
            params['access_token'] = self.access_token
            if method.upper() == 'GET':
                response = requests.get(url, params=params)
            else:
                response = requests.post(url, params=params, data=payload, headers={'Content-Type': 'application/json'})
            result = response.json()
            
        return result

    # ==========================================
    # 1. 自定义菜单管理 (Custom Menu)
    # ==========================================
    def create_menu(self, menu_data: dict) -> dict:
        """创建自定义菜单"""
        return self._request('POST', '/cgi-bin/menu/create', data=menu_data)
        
    def get_menu(self) -> dict:
        """查询自定义菜单"""
        return self._request('GET', '/cgi-bin/menu/get')
        
    def delete_menu(self) -> dict:
        """删除自定义菜单"""
        return self._request('GET', '/cgi-bin/menu/delete')

    # ==========================================
    # 2. 草稿箱管理 (Draft Management)
    # ==========================================
    def add_draft(self, articles: List[dict]) -> dict:
        """新建草稿"""
        return self._request('POST', '/cgi-bin/draft/add', data={"articles": articles})
        
    def get_draft(self, media_id: str) -> dict:
        """获取草稿"""
        return self._request('POST', '/cgi-bin/draft/get', data={"media_id": media_id})
        
    def delete_draft(self, media_id: str) -> dict:
        """删除草稿"""
        return self._request('POST', '/cgi-bin/draft/delete', data={"media_id": media_id})
        
    def update_draft(self, media_id: str, index: int, article: dict) -> dict:
        """修改草稿"""
        data = {
            "media_id": media_id,
            "index": index,
            "articles": article
        }
        return self._request('POST', '/cgi-bin/draft/update', data=data)
        
    def get_draft_count(self) -> dict:
        """获取草稿总数"""
        return self._request('GET', '/cgi-bin/draft/count')
        
    def batch_get_draft(self, offset: int = 0, count: int = 20, no_content: int = 0) -> dict:
        """获取草稿列表"""
        data = {
            "offset": offset,
            "count": count,
            "no_content": no_content
        }
        return self._request('POST', '/cgi-bin/draft/batchget', data=data)

    # ==========================================
    # 3. 发布能力 (Publish Management)
    # ==========================================
    def submit_publish(self, media_id: str) -> dict:
        """发布接口"""
        return self._request('POST', '/cgi-bin/freepublish/submit', data={"media_id": media_id})
        
    def get_publish_status(self, publish_id: str) -> dict:
        """发布状态轮询接口"""
        return self._request('POST', '/cgi-bin/freepublish/get', data={"publish_id": publish_id})
        
    def delete_publish(self, article_id: str, index: int = 0) -> dict:
        """删除发布"""
        data = {
            "article_id": article_id,
            "index": index
        }
        return self._request('POST', '/cgi-bin/freepublish/delete', data=data)
        
    def get_publish_article(self, article_id: str) -> dict:
        """通过 article_id 获取已发布文章"""
        return self._request('POST', '/cgi-bin/freepublish/getarticle', data={"article_id": article_id})
        
    def batch_get_publish(self, offset: int = 0, count: int = 20, no_content: int = 0) -> dict:
        """获取成功发布列表"""
        data = {
            "offset": offset,
            "count": count,
            "no_content": no_content
        }
        return self._request('POST', '/cgi-bin/freepublish/batchget', data=data)

    # ==========================================
    # 4. 素材管理 (Asset Management)
    # ==========================================
    def get_material(self, media_id: str) -> dict:
        """获取永久素材"""
        return self._request('POST', '/cgi-bin/material/get_material', data={"media_id": media_id})
        
    def delete_material(self, media_id: str) -> dict:
        """删除永久素材"""
        return self._request('POST', '/cgi-bin/material/del_material', data={"media_id": media_id})
        
    def get_material_count(self) -> dict:
        """获取素材总数"""
        return self._request('GET', '/cgi-bin/material/get_materialcount')
        
    def batch_get_material(self, type: str, offset: int = 0, count: int = 20) -> dict:
        """获取素材列表 (type: image, video, voice, news)"""
        data = {
            "type": type,
            "offset": offset,
            "count": count
        }
        return self._request('POST', '/cgi-bin/material/batchget_material', data=data)

    # ==========================================
    # 5. 用户管理 (User Management)
    # ==========================================
    def get_user_list(self, next_openid: str = "") -> dict:
        """获取用户列表"""
        params = {"next_openid": next_openid} if next_openid else {}
        return self._request('GET', '/cgi-bin/user/get', params=params)
        
    def get_user_info(self, openid: str, lang: str = "zh_CN") -> dict:
        """获取用户基本信息"""
        params = {"openid": openid, "lang": lang}
        return self._request('GET', '/cgi-bin/user/info', params=params)
        
    def update_user_remark(self, openid: str, remark: str) -> dict:
        """设置用户备注名"""
        data = {"openid": openid, "remark": remark}
        return self._request('POST', '/cgi-bin/user/info/updateremark', data=data)

    # ==========================================
    # 6. 留言管理 (Comments Management)
    # ==========================================
    def open_comment(self, msg_data_id: int, index: int = 0) -> dict:
        """打开已群发文章留言"""
        data = {"msg_data_id": msg_data_id, "index": index}
        return self._request('POST', '/cgi-bin/comment/open', data=data)
        
    def close_comment(self, msg_data_id: int, index: int = 0) -> dict:
        """关闭已群发文章留言"""
        data = {"msg_data_id": msg_data_id, "index": index}
        return self._request('POST', '/cgi-bin/comment/close', data=data)
        
    def get_comment_list(self, msg_data_id: int, index: int = 0, begin: int = 0, count: int = 50, type: int = 0) -> dict:
        """查看指定文章的留言数据 (type: 0普通, 1精选)"""
        data = {
            "msg_data_id": msg_data_id,
            "index": index,
            "begin": begin,
            "count": count,
            "type": type
        }
        return self._request('POST', '/cgi-bin/comment/list', data=data)
        
    def mark_elect_comment(self, msg_data_id: int, index: int, user_comment_id: int) -> dict:
        """将留言标记精选"""
        data = {"msg_data_id": msg_data_id, "index": index, "user_comment_id": user_comment_id}
        return self._request('POST', '/cgi-bin/comment/markelect', data=data)
        
    def unmark_elect_comment(self, msg_data_id: int, index: int, user_comment_id: int) -> dict:
        """将留言取消精选"""
        data = {"msg_data_id": msg_data_id, "index": index, "user_comment_id": user_comment_id}
        return self._request('POST', '/cgi-bin/comment/unmarkelect', data=data)
        
    def delete_comment(self, msg_data_id: int, index: int, user_comment_id: int) -> dict:
        """删除留言"""
        data = {"msg_data_id": msg_data_id, "index": index, "user_comment_id": user_comment_id}
        return self._request('POST', '/cgi-bin/comment/delete', data=data)
        
    def reply_comment(self, msg_data_id: int, index: int, user_comment_id: int, content: str) -> dict:
        """回复留言"""
        data = {
            "msg_data_id": msg_data_id,
            "index": index,
            "user_comment_id": user_comment_id,
            "content": content
        }
        return self._request('POST', '/cgi-bin/comment/reply/add', data=data)
        
    def delete_reply(self, msg_data_id: int, index: int, user_comment_id: int) -> dict:
        """删除回复"""
        data = {"msg_data_id": msg_data_id, "index": index, "user_comment_id": user_comment_id}
        return self._request('POST', '/cgi-bin/comment/reply/delete', data=data)

    # ==========================================
    # 7. 基础消息与群发 (Basic Messages & Batch Sends)
    # ==========================================
    def send_custom_message(self, touser: str, msgtype: str, **kwargs) -> dict:
        """发送客服消息 (被动回复之外的普通消息)"""
        data = {"touser": touser, "msgtype": msgtype}
        data.update(kwargs)
        return self._request('POST', '/cgi-bin/message/custom/send', data=data)
        
    def send_mass_message(self, filter_is_to_all: bool, filter_tag_id: int, msgtype: str, **kwargs) -> dict:
        """根据标签进行群发"""
        data = {
            "filter": {"is_to_all": filter_is_to_all, "tag_id": filter_tag_id},
            "msgtype": msgtype
        }
        data.update(kwargs)
        return self._request('POST', '/cgi-bin/message/mass/sendall', data=data)

    # ==========================================
    # 8. 客服管理 (Customer Service)
    # ==========================================
    def add_kf_account(self, kf_account: str, nickname: str, password: str) -> dict:
        """添加客服账号"""
        data = {"kf_account": kf_account, "nickname": nickname, "password": password}
        return self._request('POST', '/customservice/kfaccount/add', data=data)
        
    def get_kf_list(self) -> dict:
        """获取所有客服账号"""
        return self._request('GET', '/cgi-bin/customservice/getkflist')

    # ==========================================
    # 9. 数据统计 (Data Statistics)
    # ==========================================
    def get_article_summary(self, begin_date: str, end_date: str) -> dict:
        """获取图文群发每日数据"""
        data = {"begin_date": begin_date, "end_date": end_date}
        return self._request('POST', '/datacube/getarticlesummary', data=data)
        
    def get_user_summary(self, begin_date: str, end_date: str) -> dict:
        """获取用户增减数据"""
        data = {"begin_date": begin_date, "end_date": end_date}
        return self._request('POST', '/datacube/getusersummary', data=data)

# ==========================================
# OpenClaw Skill 接口定义
# ==========================================

def wechat_manage_capability(app_id: str, app_secret: str, capability: str, action: str, **kwargs) -> dict:
    """
    [OpenClaw Skill] 微信公众号能力管理统一接口。
    支持：自定义菜单(menu)、草稿箱(draft)、发布能力(publish)、素材管理(material)、用户管理(user)、留言管理(comment)、基础消息(message)、客服(kf)、数据统计(analysis)。
    
    Args:
        app_id (str): 微信公众号 AppID
        app_secret (str): 微信公众号 AppSecret
        capability (str): 能力模块，可选值：'menu', 'draft', 'publish', 'material', 'user', 'comment', 'message', 'kf', 'analysis'
        action (str): 执行的动作，例如 'create', 'get', 'delete', 'add', 'update', 'list', 'reply' 等
        **kwargs: 其他动作所需的参数
        
    Returns:
        dict: 微信 API 的响应结果
    """
    manager = WeChatCapabilityManager(app_id, app_secret)
    
    try:
        if capability == 'menu':
            if action == 'create': return manager.create_menu(kwargs.get('menu_data', {}))
            elif action == 'get': return manager.get_menu()
            elif action == 'delete': return manager.delete_menu()
            
        elif capability == 'draft':
            if action == 'add': return manager.add_draft(kwargs.get('articles', []))
            elif action == 'get': return manager.get_draft(kwargs.get('media_id'))
            elif action == 'delete': return manager.delete_draft(kwargs.get('media_id'))
            elif action == 'update': return manager.update_draft(kwargs.get('media_id'), kwargs.get('index', 0), kwargs.get('article', {}))
            elif action == 'count': return manager.get_draft_count()
            elif action == 'batchget': return manager.batch_get_draft(kwargs.get('offset', 0), kwargs.get('count', 20), kwargs.get('no_content', 0))
            
        elif capability == 'publish':
            if action == 'submit': return manager.submit_publish(kwargs.get('media_id'))
            elif action == 'get_status': return manager.get_publish_status(kwargs.get('publish_id'))
            elif action == 'delete': return manager.delete_publish(kwargs.get('article_id'), kwargs.get('index', 0))
            elif action == 'get_article': return manager.get_publish_article(kwargs.get('article_id'))
            elif action == 'batchget': return manager.batch_get_publish(kwargs.get('offset', 0), kwargs.get('count', 20), kwargs.get('no_content', 0))
            
        elif capability == 'material':
            if action == 'get': return manager.get_material(kwargs.get('media_id'))
            elif action == 'delete': return manager.delete_material(kwargs.get('media_id'))
            elif action == 'count': return manager.get_material_count()
            elif action == 'batchget': return manager.batch_get_material(kwargs.get('type', 'image'), kwargs.get('offset', 0), kwargs.get('count', 20))
            
        elif capability == 'user':
            if action == 'get_list': return manager.get_user_list(kwargs.get('next_openid', ''))
            elif action == 'get_info': return manager.get_user_info(kwargs.get('openid'), kwargs.get('lang', 'zh_CN'))
            elif action == 'update_remark': return manager.update_user_remark(kwargs.get('openid'), kwargs.get('remark'))
            
        elif capability == 'comment':
            msg_data_id = kwargs.get('msg_data_id')
            index = kwargs.get('index', 0)
            user_comment_id = kwargs.get('user_comment_id')
            
            if action == 'open': return manager.open_comment(msg_data_id, index)
            elif action == 'close': return manager.close_comment(msg_data_id, index)
            elif action == 'list': return manager.get_comment_list(msg_data_id, index, kwargs.get('begin', 0), kwargs.get('count', 50), kwargs.get('type', 0))
            elif action == 'markelect': return manager.mark_elect_comment(msg_data_id, index, user_comment_id)
            elif action == 'unmarkelect': return manager.unmark_elect_comment(msg_data_id, index, user_comment_id)
            elif action == 'delete': return manager.delete_comment(msg_data_id, index, user_comment_id)
            elif action == 'reply': return manager.reply_comment(msg_data_id, index, user_comment_id, kwargs.get('content'))
            elif action == 'delete_reply': return manager.delete_reply(msg_data_id, index, user_comment_id)
            
        elif capability == 'message':
            if action == 'send_custom': return manager.send_custom_message(kwargs.get('touser'), kwargs.get('msgtype'), **kwargs.get('msg_data', {}))
            elif action == 'send_mass': return manager.send_mass_message(kwargs.get('filter_is_to_all', True), kwargs.get('filter_tag_id', 0), kwargs.get('msgtype'), **kwargs.get('msg_data', {}))
            
        elif capability == 'kf':
            if action == 'add': return manager.add_kf_account(kwargs.get('kf_account'), kwargs.get('nickname'), kwargs.get('password'))
            elif action == 'get_list': return manager.get_kf_list()
            
        elif capability == 'analysis':
            if action == 'get_article_summary': return manager.get_article_summary(kwargs.get('begin_date'), kwargs.get('end_date'))
            elif action == 'get_user_summary': return manager.get_user_summary(kwargs.get('begin_date'), kwargs.get('end_date'))
            
        return {"errcode": -1, "errmsg": f"不支持的能力或动作: {capability} -> {action}"}
        
    except Exception as e:
        return {"errcode": -1, "errmsg": str(e)}
