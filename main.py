import mitmproxy.http
import asyncio
from requests_toolbelt.multipart.encoder import MultipartEncoder
from mitmproxy.options import Options
from mitmproxy.tools import dump
import mitmproxy.http

class Action1:
    def __init__(self):
        self.url = ""
    #拦截发出的请求函数
    def request(self, flow: mitmproxy.http.HTTPFlow):
        self.url = flow.request.url

        if "https://jstxcj.91job.org.cn/v2/camera/upload" == self.url:
            new_fields = []
            for name, value in flow.request.multipart_form.items(multi=True):
                if name != b"file":
                    new_fields.append((name, value))
            files = {
                "file": ("tmp.jpg", open("pyy.jpg", "rb"), "image/jpeg"),
                "type": new_fields[0][1].decode(),
                "code": new_fields[1][1].decode(),
            }

            content_type = flow.request.headers.get("Content-Type", "")
            boundary = content_type.split("boundary=")[-1]

            encoder = MultipartEncoder(fields=files, boundary=boundary)

            # 修改请求体和 headers
            flow.request.content = encoder.to_string()
            flow.request.headers["Content-Type"] = encoder.content_type

    def response(self, flow: mitmproxy.http.HTTPFlow):
        if "https://jstxcj.91job.org.cn/code/decode" == self.url:
            token = flow.response.text
            print("解码返回的 token:", token)
            with open("token.txt", "w") as f:
                f.write(token.replace('"', ""))

        if "https://jstxcj.91job.org.cn/v2/camera/upload" == self.url:
            print("图片上传返回:", flow.response.text)
            print("图片上传返回json:", flow.response.json())


addons = [Action1()]

if __name__ == "__main__":
    async def func_temp(host, port):
        opts = Options(listen_host=host, listen_port=port, ssl_insecure=True)
        dm = dump.DumpMaster(opts, with_termlog=True, with_dumper=False)
        dm.addons.add(Action1())

        try:
            await dm.run()
        except BaseException as e:
            print(e)
            dm.shutdown()


    asyncio.run(func_temp('0.0.0.0', 8085))