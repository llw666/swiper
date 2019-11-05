from django.http import JsonResponse
from django.core.cache import cache
from user.logics import send_vcode
from common import keys
from user.models import User

def get_vcode(request):
    '''用户获取验证码接口'''
    phonenum = request.GET.get('phonenum')
    result = send_vcode(phonenum)
    if result:
        return JsonResponse({'code': 0, 'data': None})
    else:
        return JsonResponse({'code': 1000, 'data': None})


def submit_vcode(request):
    '''用户提交验证码, 并执行登陆或注册'''
    # 获取参数
    phonenum = request.POST.get('phonenum')
    vcode = request.POST.get('vcode')

    # 从缓存获取上一步保存的验证码
    cached_vcode = cache.set(keys.VCODE % phonenum, vcode, 180)  # 将验证码添加到缓存

    # 检查验证码
    if vcode and cached_vcode and vcode == cached_vcode:
        # 登录或注册
        try:
            # 用户存在的情况
            user = User.objects.get(phonenum=phonenum)
        except User.DoesNotExist:
            # 用户不存在的情况，直接创建
            user = User.objects.create(phonenum=phonenum, nickname=phonenum)

        # 将用户状态记录到 Session
        request.session['uid'] = user.id
        return JsonResponse({'code': 0,'data': user.to_dict()})
    else:
        return JsonResponse({'code': 1001, 'data': None})

