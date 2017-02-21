# Dese

![Dese](https://raw.githubusercontent.com/AielloChan/pywallpaper/master/logo.ico)

`Windows` 上可自动设置背景桌面的小程序。可以将大多数的 `JSON API` 中的图片链接作为自己
的 Windows wallpaper，现已经包含以下网站图片的配置文件：

- [bing每日一图](https://bing.com)
- [百度图片](https://images.baidu.com)
- [Unsplash](https://unsplash.com)
- [爱壁纸](http://aibizhi.com)

虽然现在网上各种设置背景的软件数不胜数，但是又有几个是不会在后台悄悄运行或者跳出广告的呢？
开发这个软件一是为了在学 `Python` 时练手，增加动力；二是想要一个可配置的、具有大量高质
图片资源、运行完就干干净净退出的程序。

*注：不可将其用于任何的商业目的！*

# 使用方法

*可使用PyInstaller进行打包*

## 方法一

双击运行 `Dese.exe`

## 方法二

命令行切换到当前目录后，输入以下命令：

```bash
python main.py
```
即可运行。

# 进阶配置

图片来源是可以通过配置文件进行配置的，以下是配置文件所有字段的定义：

| 字段                                          | 可选值                                                  | 描述                                                    |
| -------------                                 |:-------------                                          | -----:                                                  |
| [api_url](#api_url)                           | 任意                                                    | 一个可以获得 `JSON` 格式的 API URL                       |
| [picture_url_locat](#picture_url_locat)       | "key"、"[number]"、"[start~end]"                        | 一种 `JSON` 位置的表述方式                               | 
| [picture_url_host](#picture_url_host)         | host 如 "http://baidu.com"                              | 指定下载图片时所使用的 host                              | 
| [name_type](#name_type)                       | "url"、"time"、"json"                                   | 图片文件的命名方式                                       |
| [name_exclude_char](#name_exclude_char)       | 任意字符                                                | 图片名称中需要去掉的字符                                  |
| [name_fill_char](#name_fill_char)             | 任意字符                                                | 去掉字符时可选择用此值来填充                              | 
| [wallpaper_fill_type](#wallpaper_fill_type)   | "fill"、"fit"、"Stretch"、"tile"、"center"、"span"      | 背景填充方式                                             |
| [picture_store_path](#picture_store_path)     | 相对目录 如 "pics" 或绝对目录 如 "E:/wallpaper"          | 背景图片存放目录，可为相对目录或绝对目录                    |
| [picture_postfix](#picture_postfix)           | 任意后缀或者为空                                         | 下载图片时的后缀，如果所选择的命名方式中不存在后缀则在此添加 |


## api_url

这个是 API 的地址，要求必须是返回 `JSON` 格式的数据。如 bing 的 API，百度图片的 API，
爱壁纸的 API 以及 Unsplash 的 API。

## picture_url_locat

一种特殊的 `JSON` 对象选择描述方式，例如以下 `JSON` 对象：

```json
{
    "name": "baidu",
    "data": [
        {
            "url": "http://baidu.com/xxx1.jpg",
            "level": "6"
        },
        {
            "url": "http://baidu.com/xxx2.jpg",
            "level": "2"
        },
        {
            "url": "http://baidu.com/xxx3.jpg",
            "level": "2"
        }
    ]
}
```

| `picture_url_locat` 值 | 效果                       |
| --------               | --------                  |
| "name"                 | 获取 `name` 的值，也就是 `baidu`           |  
| "data [0] url"         | 获取 `data` 数组中索引为 `0` 的元素的 `url` 字段值，此处即获得了 `http://baidu.com/xxx1.jpg` 这个 URL|
| "data [0~2] url"       | 获取 `data` 数组中索引为 `0` 到 `2` 的**随机数**元素的 `url` 字段值，在这里我们只能确定他最终获取的是一个 URL|
| "data [~] url"         | 获取 `data` 数组中小于其长度的**随机数**索引对应元素的 `url` 字段值，在这里我们只能确定他最终获取的是一个 URL|

简单吧？

## picture_url_host

当 `JSON` 中的下载链接是以 `/` 开头，并没有 `host` 信息的，程序会自动将当前 `API` 的 
`host` 添加在其前面组成一个完整的下载链接。但是有的下载链接 `host` 并不是当前 `API` 的
 `host`，这个时候我们就需要手动指定这个 `host` 值，也就是 `picture_url_host` 的值。

## name_type

命名的类型，总共有三种方式：`url`、`json`、`time`。
- `url` 是截取图片下载链接最后
  一部分作为文件名（在最后一个`/`之后，`?`之前），如选择的图片链接为 
  `http://baidu.com/xxx1.jpg?size=2k`，则截取到的文件名为 `xxx1.jpg`。
- `json` 则接收和 `picture_url_locat` 字段一样的参数，从 `json` 中获取文件名
- `time` 则是以下载图片时的时间（时间戳）作为文件名。


## name_exclude_char

这个字段在 `name_type` 为 `json` 或 `url` 时必须填写（可为空字符串""）。表示需要从
文件名中剔除的字符，这是为了防止特殊字符在 Windows 系统中造成乱码。多个字符直接连在一起
即可，如：我要去除文件名中的 `@` 和 `"` 符号，`name_exclude_char` 的值就应为 `"@\""`。

## name_fill_char

此字段在 `name_exclude_char` 字段填写后生效，当 `name_exclude_char` 中规定的字符被剔
除时，会使用当前字段定义的字符来填充。如：

原始文件名为：`12315*43@2.jpg`，`name_exclude_char` 值为 `"*@"`，`name_fill_char` 
值为 `__`，则最为后的文件名为 `12315__43__2.jpg`

## wallpaper_fill_type

背景的填充方式，对应 Windows 10 `设置->个性化->背景->契合度` 中的值。默认为 `fill`。

## picture_store_path

图片的存放路径，默认为 `pics`， 绝对目录以及相对目录均可。如 `E:/wallpaper`。*注：
*路径用 `/` 分隔而不是 `\`。

## picture_postfix

图片名字的后缀，如果你的图片下载链接中不存在文件后缀（如 `htt://baidu.com/xxx1`），
或者 `name_type` 选择的是 `time` ，则需要将此字段填写为 ".jpg"。不过如果你的文件名中已有
后缀（如 `http://baidu.com/xxx1.jpg`），则将此字段的值设置为 `""`。此字段不可省略。

# 示例

以下是一部分的 `config.json` 配置：

- [Unsplash](https://unsplash.com)

  ```json
  {
    "api_url": "https://api.unsplash.com/photos/random?client_id=此处填写你自己的应用ID",
    "picture_url_locat": "urls full",
    "name_type": "url",
    "wallpaper_fill_type": "fill",
    "picture_store_path": "pics/",
    "picture_postfix": ".jpg"
  }
  ```
- [爱壁纸](http://lovebizhi.com)

  ```json
  {
    "api_url": "http://api.lovebizhi.com/macos_v4.php?a=category&tid=2&uuid=436e4ddc389027ba3aef863a27f6e6f9&retina=1&bizhi_width=1920&bizhi_height=1200&client_id=1008",
    "picture_url_locat": "data [0~60] image diy",
    "name_type": "url",
    "wallpaper_fill_type": "fill",
    "picture_store_path": "pics/",
    "picture_postfix": ""
  }
  ```
- [百度图片](https://image.baidu.com)

  ```json
  {
    "api_url": "http://image.baidu.com/channel/listjson?tag1=%E5%A3%81%E7%BA%B8&tag2=%E9%A3%8E%E6%99%AF&pn=0&rn=50",
    "picture_url_locat": "data [0~50] image_url",
    "name_type": "url",
    "wallpaper_fill_type": "fill",
    "picture_store_path": "pics/",
    "picture_postfix": ""
  }
  ```
- [Bing每日壁纸](https://bing.com)

  ```json
  {
    "api_url": "http://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=8",
    "picture_url_locat": "images [0] url",
    "name_type": "url",
    "wallpaper_fill_type": "fill",
    "picture_store_path": "pics/",
    "picture_postfix": ""
  }
  ```