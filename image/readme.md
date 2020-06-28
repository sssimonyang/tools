## 用python进行图片整理

图片整理的基础是区分拍摄图片和表情包、截图之类的其他图片。在此，我们使用`exif`信息对拍摄图片和其他图片进行区分。

对`exif`信息进行一下简单介绍。

### Exif

**可交换图像文件格式**（英语：Exchangeable image file format，官方简称**Exif**），是专门为[数码相机](https://baike.baidu.com/item/数码相机)的照片设定的，可以记录数码照片的属性信息和拍摄数据。

`exif`的常见形式为，手机上你拍照时照片同时记录下的gps位置信息和拍照时间，数码相机存储的拍照时间。在手机上查看图片时有一个详情选项，如果记录了gps位置信息和拍照时间就会显示。同时，手机相册也会根据此信息进行照片展示和分类。

下图为一个例子：![IMG_20200628_191101](https://gitee.com/sssimonyang/images/raw/master/20200628191147.jpg)

> 值得注意的是，聊天软件（QQ、Wechat等）在发送图片时可能会发送图片的完整信息，即，对方在收到图片后能够通过技术手段获得你的定位。在测试时，我们发现苹果的发送后图片，其定位和拍摄时间等信息均消失，而在小米手机上，MIUI12注意到了此问题，在发送图片时可以进行信息是否抹除选项的选择，而MIUI之前的系统均存在此问题。
>
> 因此，建议大家，尤其是**女生**，在发送给陌生人图片时谨慎一些，注意隐私保护。此处给MIUI12打call。

![QQ图片20200628191805](https://gitee.com/sssimonyang/images/raw/master/20200628192004.jpg)

当我们知道了`exif`信息中存在图片拍摄时间后，稍加搜索，便可以知道python的`exifread`库可以进行图片拍摄时间的提取。因此，整个项目的完成就是可预期的。

### 思路

在对图片进行整理时，考虑将存在拍摄时间的放在一起，将不存在拍摄时间的放在一起，然后对存在时间信息的图片根据年月进行分区。同时，在整个待处理文件夹中也可能存在一些乱入的word、视频文件。也因为大文件可能对我们更重要，小文件则相对来说更多，但是可能都是一些无用的聊天表情包之类的。因此也根据文件类型以及文件大小进行区分。

最终，第一层的文件夹结构如下：

```
-after_arrangement
	-img
		-big_withouttime
		-big_withtime
		-small
	-other
	-video
		-big
		-small
```

生成大类目录：

```python
file_category = ['img', 'video', 'other', 'video/big', 'video/small', 'img/big_withtime', 'img/big_withouttime','img/small']

def makedirs(file_category):
    for category in file_category:
        directory = os.path.join(*category.split('/'))
        if not os.path.exists(directory):
            os.mkdir(directory)
```

其中，`category`使用`/`拆分之后解包使用`join`连接。

### 生成目录

我们想将存有拍摄时间的图片分到对应文件夹里，比如2020年06月放到`2020/06`文件夹下，但是同时又不想让空的文件夹存在。如果我们在对每个文件获得时间后再查看是否存在对应的年月文件夹，在不存在时创建，其运行次数将等于照片数目，这增加了运行时间。因此，我们考虑预先生成所有年月文件夹。在此处，我们主要是在`big_withtime`目录下生成这些文件夹。

```python
time_dir = 'img/big_withtime'

def timedir_prepare(timedir):
    timedir = os.path.join(*timedir.split('/'))
    for i in range(1998, time.localtime().tm_year + 1):
        directory = os.path.join(timedir, f'{i}')
        if not os.path.exists(directory):
            os.mkdir(directory)

        for j in range(1, 13):
            directory = os.path.join(timedir, f'{i}', f'{j:02}')
            if not os.path.exists(directory):
                os.mkdir(directory)
```

`timedir_prepare`函数主要是生成从1998（我的出生年，不可能有更早的照片了哈哈）到今年的每年12个月对应的文件夹。

这样生成之后，图片直接储存，就不用担心对应的文件夹是否存在的问题了。

### 删除目录

我们生成了充分多的目录，很显然，不是所有的目录都会有文件。为了便于之后的查看，我们希望空目录是不存在的。因此，写一个`timedir_end`函数，对上述所有文件夹进行从下往上的遍历，当不存在文件时，删除该文件夹。

```python
def timedir_end(timedir):
    timedir = os.path.join(*timedir.split('/'))
    for i in range(1998, time.localtime().tm_year + 1):
        for j in range(1, 13):
            directory = os.path.join(timedir, f'{i}', f'{j:02}')
            if not os.listdir(directory):
                os.rmdir(directory)
    for i in range(1998, time.localtime().tm_year + 1):
        directory = os.path.join(timedir, f'{i}')
        if not os.listdir(directory):
            os.rmdir(directory)
```

注意此处的先后顺序，先删除月，后年才能因为没有内部文件夹而被删除。

### 获取图片时间

首先，通过命令安装`exifread`库：

```shell
pip install exifread
```

搜索找个示例用一下

```python
def process_img(path):
    '''
    这个函数用来处理图片 并返回图片的 经纬度、拍摄时间信息
    :return: 返回图片信息 是一个字典
    '''
    f = open(path, 'rb')
    tags = exifread.process_file(f)
    info = {
        # 注意 这里获得到的是值 需要使用 values方法
        'Image DateTime(拍摄时间)': tags.get('Image DateTime', '0').values,
        'GPS GPSLatitudeRef(纬度标志)': tags.get('GPS GPSLatitudeRef', '0').values,
        'GPS GPSLatitude(纬度)': tags.get('GPS GPSLatitude', '0').values,
        'GPS GPSLongitudeRef(经度标志)': tags.get('GPS GPSLongitudeRef', '0').values,
        'GPS GPSLongitude(经度)': tags.get('GPS GPSLongitude', '0').values
    }
    return info
```

> 代码来源于CSDN博主「大隐.」的原创文章，遵循CC 4.0 BY-SA版权协议，[CSDN原文链接](https://blog.csdn.net/weixin_42218582/article/details/90732231)

显然这个信息过多，我们只需要时间就够了。

```python
def get_photo_time(file):
    f = open(file, 'rb')
    tags = exifread.process_file(f)
    photo_time = tags.get('Image DateTime').values
    return photo_time
```

但是可以预知的是，不是所有的图片都存在`exif`信息，也有可能`exif`信息里没有时间，对这种情况我们希望返回`None`。同时，我们最后所用到的只有年和月，因此需要对类似`2019:03:28 21:08:36`形式的信息进行提取后加工。

更改后如下：

```python
def get_photo_time(file):
    f = open(file, 'rb')
    tags = exifread.process_file(f)
    if tags and 'Image DateTime' in tags:
        photo_time = tags.get('Image DateTime').values
        return time.strftime('%Y/%m', time.strptime(photo_time, '%Y:%m:%d %H:%M:%S'))
    return None
```

该函数的返回值则类似`2019/03`形式，是我们所期望的。

### 文件移动

在找到文件并且知道他该去哪的时候，就需要进行文件的复制或移动。稍加搜索便可以知道`shutil`库可以解决该问题。

主要使用的函数为复制`shutil.copyfile`，移动`shutil.move`，参数为原路径和新路径。

在移动时根据参数进行文件路径的拼接生成，因此函数如下。

```python
def move(to_where, file_path, ext, remove=False, photo_time=None):
    if to_where.endswith('withtime') and photo_time:
        to_file_path = os.path.join(*to_where.split('/'), *photo_time.split('/'))
    else:
        to_file_path = os.path.join(*to_where.split('/'))
    if remove:
        shutil.move(file_path,
                    os.path.join(f'{to_file_path}', f'{len(os.listdir(to_file_path)) + 1:03}') + '.' + ext)
    else:
        shutil.copyfile(file_path,
                        os.path.join(f'{to_file_path}', f'{len(os.listdir(to_file_path)) + 1:03}') + '.' + ext)
```

其中，`to_where`是类似`img/big_withtime`的形式，`file_path`是原文件的地址，`ext`是文件后缀名，`remove`可以控制是否保留原文件，`photo_time`信息由`get_photo_time`函数获得。文件的命名采取顺序命名，三位靠右填充0，当`num=1`时`{num:03}`呈现出`001`的形式。

### 文件夹遍历

稍加搜索，遍历的实现库函数是`os.walk`，该函数默认从上到下（`topdown=False`时从下到上）遍历每一个文件夹，返回`root dirs files`

- root  str，当前正在遍历的文件夹的地址
- dirs  list，该文件夹中所有的目录
- files  list,  该文件夹中所有的文件

先写出如下函数：

```python
def main(process_directory, to_directory, remove=False):
    curdir = os.path.abspath(os.curdir)
    os.chdir(to_directory)
    makedirs(file_category)
    timedir_prepare(time_dir)
    for root, dirs, files in os.walk(process_directory):
        process_files(root, files, remove)
    timedir_end(time_dir)
    os.chdir(curdir)
```

因为之后的处理都是类似`img/big_withtime`的目录名，因此首先保留当前运行目录，切换至目标写入目录，最后切换回来。中间先生成第一级目录，然后生成年月目录。

对于处理该目录下所有文件的函数`process_files`还没写，主要的工作是完成类型鉴定，以及指定`move`需要的`to_where`。我们主要依靠文件的后缀名进行文件分类，但是考虑到后缀名可能是大写的以及`jpg png bmp`均为`img`，因此，此处需要对后缀名删除点号后变小写再进行映射。

```python
format_map = {'jpg': 'img',
              'jpeg': 'img',
              'png': 'img',
              'bmp': 'img',
              'gif': 'img',
              'mp4': 'video'}
def process_files(root, files, remove):
    for file in files:
        file_path = os.path.join(root, file)
        ext = os.path.splitext(file_path)[1][1:].lower()
        if ext not in format_map.keys():
            file_type = input(f"{ext}属于何种类型：")
            while file_type not in ['img', 'video', 'other']:
                print(f"请输入img或video或other")
                file_type = input(f"{ext}属于何种类型：")
            format_map[ext] = file_type
        photo_time = None
        to_where = ''
        if format_map[ext] == 'img':
            if os.path.getsize(file_path) >= 1024 ** 2:
                photo_time = get_photo_time(file_path)
                if photo_time:
                    to_where = 'img/big_withtime'
                else:
                    to_where = 'img/big_withouttime'
            else:
                to_where = 'img/small'
        if format_map[ext] == 'video':
            if os.path.getsize(file_path) >= 1024 ** 2:
                to_where = 'video/big'
            else:
                to_where = 'video/small'
        if format_map[ext] == 'other':
            to_where = 'other'
        move(to_where, file_path, ext, remove, photo_time)
```

`while`部分主要解决出现预知不到的类型的问题，出现时可以手动指示该文件是`img video other`中的哪一种，使软件能够应对突如其来的其他类型文件。然后主要根据获得的文件后缀名`ext`以及文件是否大于1024^2(1M)来进行文件夹的选择，最后使用move进行具体文件操作。

### 完善

项目需要的大部分操作都已完成，但是，思考一下，如果每次遇见新文件都要你手动输入类型，那太烦了，如果软件具有记忆功能就好了。我们选择使用`json`作为`format_map`信息文件存储的形式，在你手动输入陌生后缀名对应的类型后，`json`文件便会增加一条记录。当再次运行该软件时，就不用再次输入了。同时，为了便于使用，我们采用`argparse`库进行命令行参数解析。

```python
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--dir", help="specify the image directory you want to process")
    parser.add_argument("-o", "--out", help="specify the directory to store file, empty is recommended")
    parser.add_argument("-remove", "--remove", help="remove the raw file or false", action="store_true")
    args = parser.parse_args()
    with open('format.json', 'r') as f:
        format_map = json.load(f)
    main(args.dir, args.out, args.remove)
    with open('format.json', 'w') as f:
        json.dump(format_map, f, indent=2)
```

命令行运行，当最后添加`-remove`时，表示需要删除原文件。

```powershell
python image_arrangement.py -d C:\Users\sssimonyang\Pictures\before_arrangement -o C
:\Users\sssimonyang\Pictures\after_arrangement
```

### bug fix

在运行时出现了一些错误，主要问题在`exif`信息处理。

![QQ截图20200628165805](https://gitee.com/sssimonyang/images/raw/master/20200628203305.jpg)

这个日期后面还带个下午就很有意思，但是也没有办法。

同时也有存在`Image DateTime`键但是对应值为空值的情况，也对这种情况进行处理。修改后的函数如下：

```python
def get_photo_time(file):
    f = open(file, 'rb')
    tags = exifread.process_file(f)
    if tags and 'Image DateTime' in tags:
        photo_time = tags.get('Image DateTime').values
        if photo_time:
            return time.strftime('%Y/%m', time.strptime(photo_time[:19], '%Y:%m:%d %H:%M:%S'))
    return None
```

## 最后

至此，大功告成，代码文件在13:45创建，18点前已经基本完成，花费4h。代码存储在github（image文件夹，点击**阅读原文**直达）：https://github.com/sssimonyang/tools



其实，考虑到小图片中也有一些人像照片，比如说个人的历史照片、表情包之类的，其实都很有价值。未来，我们想使用`opencv`的图像识别功能对小图片进行处理，分成有人像和无人像两大类，然后对于这些`exif`信息中没有时间或者非拍摄类型的图片，其实还可以利用文件生成时间进行分类。这些可以作为进一步的工作。如果你有好的建议和想法，也欢迎提出。

