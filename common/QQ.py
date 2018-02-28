#coding=utf-8
import json
import xlwt
import xlrd
from xlutils.copy import copy  
import requests
import urllib2
import cookielib
import re,os
from bs4 import BeautifulSoup
from fileinput import filename



class SSInfo(object):

    def __init__(self, content, createTime,commentArray):
        self.content = content
        self.createTime = createTime
        self.commentArray = commentArray

        

class PicInfo(object):

    def __init__(self,desc,uploadtime,url):

        self.desc = desc

        self.uploadtime = uploadtime

        self.url = url

        

class BlogInfo(object):

    def __init__(self,pubTime,title,logId):

        self.pubTime = pubTime

        self.title = title

        self.logId = logId

        

class CommentInfo(object):

    def __init__(self,commentString):

        self.commentString = commentString



class AlbumInfo(object):

    def __init__(self,albumId,albumName):  

        self.albumId = albumId

        self.albumName = albumName 

             

class QQSpider:



    def requestHeader(self,cookie,referer,userAgent):

        cj = cookielib.CookieJar()  

        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))     

        opener.addheaders = [  

                           ('User-Agent', userAgent),

                           ('Cookie',cookie),

                           ('Referer',referer)

                          ]

        urllib2.install_opener(opener)

        return opener    

    

    def responseData(self,type,url,cookie,referer,userAgent):

        header_opener = self.requestHeader(cookie, referer, userAgent)  

        urllib2.install_opener(header_opener)

        page = header_opener.open(url)

        returnData = page.read()

        print returnData

        if type == 'blog':

            return returnData

        if type =='blogDir':

            returnData = returnData.encode('utf-8')

        identifier = '('

        nPos = returnData.index(identifier)

        jsonStr = returnData[nPos+1:]

        jsonStr= jsonStr[:-2]

        dicData = json.loads(jsonStr) 

        return  dicData     

    
    def excelStyle(self):
        style = xlwt.XFStyle()
        font = xlwt.Font()
        font.name = 'Times New Roman' #或者换成外面传进来的参数，这样可以使一个函数定义所有style
        font.bold = 'True'
#         font.height = '...'
#         font.size = '...'
#         font.colour_index('...')
        style.font = font
        
        borders = xlwt.Borders()
        borders.left = 1
        borders.right = 1
        borders.top = 1
        borders.bottom = 1
        borders.bottom_colour=0x3A    
        style.borders = borders 
        
        badBG = xlwt.Pattern()
        badBG.pattern = badBG.SOLID_PATTERN
        badBG.pattern_fore_colour = 10
        style.pattern = badBG



        alignment = xlwt.Alignment()
        alignment.horz = xlwt.Alignment.HORZ_CENTER    #水平居中
        alignment.vert = xlwt.Alignment.VERT_CENTER    #垂直居中
        style.alignment = alignment
        
        return style
    
    def blogDirSpider(self,qq,cookie,referer,userAgent):

        pageIndex = 0

        pageCount = 100

        blogDirArray = []

        bUrl = 'http://user.qzone.qq.com/p/b1.cnc/cgi-bin/blognew/get_abs?hostUin='+qq+'&uin=1239806145&blogType=0&cateName=&cateHex=&statYear=2015&reqInfo=7&pos='

        fUrl = '0&num=15&sortType=0&absType=0&source=0&rand=0.8459144670050591&ref=qzone&g_tk=1429940838&verbose=1'



        if qq=='1239806145':

            bUrl = 'http://user.qzone.qq.com/p/b11.cnc/cgi-bin/blognew/get_abs?hostUin='+qq+'&uin=1239806145&blogType=0&cateName=&cateHex=&statYear=2015&reqInfo=7&pos='

            fUrl = '&num=100&sortType=0&source=0&rand=0.9140611931215972&ref=qzone&g_tk=1779722765&verbose=1'



#         0&num=15&sortType=0&absType=0&source=0&rand=0.8459144670050591&ref=qzone&g_tk=1429940838&verbose=1

        print bUrl

        url = bUrl + str(pageIndex)+fUrl

        print url

        responseData = self.responseData('blogDir', url, cookie, referer, userAgent)

        if responseData.has_key('data'):

            if responseData['data'].has_key('totalNum'):

                totalNum = responseData['data']['totalNum']

                cicleCount = totalNum/pageCount + 1

                for i in range(cicleCount):

                    url = bUrl + str(pageIndex)+fUrl

                    responseData = self.responseData('blogDir', url, cookie, referer, userAgent)

                    listCount = len(responseData['data']['list'])

                    for j in range(listCount):

                        blogId = responseData['data']['list'][j]['blogId']

                        title = responseData['data']['list'][j]['title']

                        pubTime = responseData['data']['list'][j]['pubTime']

                        lg = BlogInfo(pubTime,title,blogId)

                        blogDirArray.append(lg)

                        print title

                    pageIndex +=pageCount;

                filename=xlwt.Workbook()

                sheet=filename.add_sheet("my_sheet")

                row = len(blogDirArray)

                print row

                for j in range(0,row):

                    xInfo = blogDirArray[j]

                    sheet.write(j,0,xInfo.pubTime)

                    sheet.write(j,1,xInfo.title)

                    sheet.write(j,2,xInfo.logId)

                filename.save("/Users/wangyanan/Desktop/日志.xls")

        return blogDirArray

    

    def blogContentSpider(self,blogArray,qq,cookie,referer,userAgent):

        for lg in blogArray:

            logId = lg.logId

#             http://b11.cnc.qzone.qq.com/cgi-bin/blognew/blog_output_data?uin=1239806145&blogid=1425552947&styledm=cnc.qzonestyle.gtimg.cn&imgdm=cnc.qzs.qq.com&bdm=b.cnc.qzone.qq.com&mode=2&numperpage=15&timestamp=1428313554&dprefix=cnc.&inCharset=gb2312&outCharset=gb2312&ref=qzone&page=1&refererurl=http%3A%2F%2Fcnc.qzs.qq.com%2Fqzone%2Fapp%2Fblog%2Fv6%2Fbloglist.html%23nojump%3D1%26page%3D1%26catalog%3Dlist

            url = 'http://b1.cnc.qzone.qq.com/cgi-bin/blognew/blog_output_data?uin='+qq+'&blogid='+str(logId)+'&styledm=cnc.qzonestyle.gtimg.cn&imgdm=cnc.qzs.qq.com&bdm=b.cnc.qzone.qq.com&mode=2&numperpage=15&timestamp=1428313554&dprefix=cnc.&inCharset=gb2312&outCharset=gb2312&ref=qzone&page=1&refererurl=http%3A%2F%2Fcnc.qzs.qq.com%2Fqzone%2Fapp%2Fblog%2Fv6%2Fbloglist.html%23nojump%3D1%26page%3D1%26catalog%3Dlist'

            responseData = self.responseData('blog', url, cookie, referer, userAgent)

            soup = BeautifulSoup(responseData)

            tc = "<head><meta http-equiv='Content-Type' content='text/html; charset=utf-8'></head>"

            findData = soup.find('div',{"class":"blog_details_20120222"})

            traverseArray = []

            if findData:

                traverseArray = findData.contents

            else:

                findData = soup.find('div',{"id":"blogDetailDiv"})

                if findData:

                    traverseArray = findData

            for x in traverseArray:

                tc +=unicode(x) 

            print lg.title

            file_object = open('/Users/wangyanan/Desktop/日志/'+str(lg.logId)+'.html', 'w')

            tc = tc.encode('utf-8')

            file_object.write(tc)

            file_object.close()

            

    def downloadPicWithUrl(self,url,fileName):

        r = requests.get(url, stream=True)

        with open(fileName, 'wb') as f: 

            for chunk in r.iter_content(chunk_size=1024):

                if chunk:

                    f.write(chunk)

        print '下载完成'

        return fileName

    

    def albumDirSpider(self,qq,cookie,referer,userAgent):

        albumDirArray = []

        url = 'http://user.qzone.qq.com/p/shalist.photo/fcgi-bin/fcg_list_album_v3?t=434225023&hostUin='+qq+'&uin=1239806145&appid=4&inCharset=utf-8&outCharset=utf-8&source=qzone&plat=qzone&format=jsonp&notice=0&filter=1&handset=4&pageNumModeSort=40&pageNumModeClass=15&needUserInfo=1&idcNum=4&callbackFun=shine0&g_tk=214491796'

#         url = 'http://user.qzone.qq.com/p/shalist.photo/fcgi-bin/fcg_list_album_v3?t=468333781&hostUin='+qq+'&uin=1239806145&appid=4&inCharset=utf-8&outCharset=utf-8&source=qzone&plat=qzone&format=jsonp&notice=0&filter=1&handset=4&pageNumModeSort=40&pageNumModeClass=15&needUserInfo=1&idcNum=4&callbackFun=shine0&g_tk=349888596'

        if qq=='1239806145':

            url = 'http://xalist.photo.qq.com/fcgi-bin/fcg_list_album_v3?g_tk=1429940838&callback=shine0_Callback&t=886826724&hostUin=1239806145&uin=1239806145&appid=4&inCharset=utf-8&outCharset=utf-8&source=qzone&plat=qzone&format=jsonp&notice=0&filter=1&handset=4&pageNumModeSort=40&pageNumModeClass=15&needUserInfo=1&idcNum=1&callbackFun=shine0&_=1428316326802'

        

        print url

        responseData = self.responseData('albumDir', url, cookie, referer, userAgent)

        if responseData.has_key('data'):

            if responseData['data'].has_key('albumListModeSort'):

                    print '1239806145'

                    albumArray = responseData['data']['albumListModeSort']

                    listCount = len(albumArray)

                    for j in range(listCount):

                        albumId = albumArray[j]['id']

                        albumName = albumArray[j]['name']

                        lg = AlbumInfo(albumId,albumName)

                        albumDirArray.append(lg)

                        print albumName

            if responseData['data'].has_key('albumListModeClass'):

                albumListArray = responseData['data']['albumListModeClass']

                listCount = len(albumListArray)

                for j in range(listCount):

                    albumArray = albumListArray[j]['albumList']

                    cListCount = len(albumArray)

                    for aj in range(cListCount):

                        albumId = albumArray[aj]['id']

                        albumName = albumArray[aj]['name']

                        lg = AlbumInfo(albumId,albumName)

                        albumDirArray.append(lg)

                        print albumName

            filename=xlwt.Workbook()

            sheet=filename.add_sheet("my_sheet")

            row = len(albumDirArray)

            print row

            for j in range(0,row):

                xInfo = albumDirArray[j]

                sheet.write(j,0,xInfo.albumName)

                sheet.write(j,1,xInfo.albumId)

            filename.save("/Users/wangyanan/Desktop/相册.xls")

        return albumDirArray 

    

    def mkdir(self,path):

        path=path.strip()

        path=path.rstrip("\\")

        isExists=os.path.exists(path)

        if not isExists:

            print path+' 创建成功'

            os.makedirs(path)

            return True

    

    def albumSpider(self,qq,cookie,referer,userAgent,albumDirArray):

        for aInfo in albumDirArray:

            albumId = aInfo.albumId

            albumName = aInfo.albumName            

            pageIndex = 0

            myDarlingData = []

            

            

            bUrl = 'http://user.qzone.qq.com/p/shplist.photo/fcgi-bin/cgi_list_photo?t=998201460&mode=0&idcNum=4&hostUin='+qq+'&topicId='+albumId+'&noTopic=0&uin=1239806145&pageStart='

            aUrl = '&pageNum=30&skipCmtCount=0&singleurl=1&batchId=&notice=0&appid=4&inCharset=utf-8&outCharset=utf-8&source=qzone&plat=qzone&outstyle=json&format=jsonp&json_esc=1&question=&answer=&callbackFun=shine0&g_tk=214491796'

            if qq =='1239806145':

                bUrl = 'http://xaplist.photo.qq.com/fcgi-bin/cgi_list_photo?g_tk=1779722765&callback=shine0_Callback&t=244606197&mode=0&idcNum=1&hostUin=1239806145&topicId='+albumId+'&noTopic=0&uin=1239806145&pageStart='

                aUrl = '&pageNum=30&skipCmtCount=0&singleurl=1&batchId=&notice=0&appid=4&inCharset=utf-8&outCharset=utf-8&source=qzone&plat=qzone&outstyle=json&format=jsonp&json_esc=1&question=&answer=&callbackFun=shine0&_=1428243144889'

            url = bUrl + str(pageIndex) + aUrl

            

            responseData = self.responseData('pic', url, cookie, referer, userAgent)

            

            if responseData.has_key('data'):

                if responseData['data'].has_key('totalInAlbum'):

                    totalAlbum = responseData['data']['totalInAlbum']

                    totalInPage = responseData['data']['totalInPage']

                    print totalAlbum,totalInPage

                    if totalAlbum == 0 or totalInPage == 0:

                        continue

                    cicleCount = totalAlbum/totalInPage + 1

                    for i in range(cicleCount):

                        responseData = self.responseData('pic', url, cookie, referer, userAgent)

                        if responseData['data'].has_key('photoList'):

                            photoListArray = responseData['data']['photoList']

                            totalInPage = responseData['data']['totalInPage']

                            if photoListArray:

                                count = len(photoListArray)

                                for j in range(count):

                                    if len(photoListArray[j]['desc'])>0:

                                        picDesc =  photoListArray[j]['desc']

                                    else:

                                        picDesc =  photoListArray[j]['name']

                                    uploadtime = photoListArray[j]['uploadtime']

                                    if len(photoListArray[j]['raw'])>0:

                                        rawPic = photoListArray[j]['raw']

                                    else:

                                        rawPic = photoListArray[j]['url']

                                    print rawPic

                                    cInfo = PicInfo(picDesc,uploadtime,rawPic)

                                    myDarlingData.append(cInfo)

                        pageIndex +=totalInPage

                        url = bUrl + str(pageIndex) + aUrl

                    totalData = len(myDarlingData)        

                    filename=xlwt.Workbook()

                    sheet=filename.add_sheet("my_sheet")

                    for row in range(0,totalData):

                        cInfo = myDarlingData[row]

                        sheet.write(row,0,cInfo.uploadtime)

                        sheet.write(row,1,cInfo.desc)

                        sheet.write(row,2,cInfo.url)

                        fileDir = "/Users/wangyanan/Desktop/相册/"+albumName+'/'

                        self.mkdir(fileDir)

                        filePath = fileDir+cInfo.uploadtime+".jpeg"

                        self.downloadPicWithUrl(cInfo.url, filePath)

    

   

    
    
       
       
       
        
    def excelRowCount(self,fileName):
        path = os.path.join(os.path.join(os.path.expanduser("~"), 'Desktop') + "/" + fileName)
        p1 = os.path.exists(path)
        print p1
        if p1:
            old_excel = xlrd.open_workbook(path, formatting_info=True)
            sheet1 = old_excel.sheet_by_index(0)
            nrows = sheet1.nrows
#             new_excel = copy(old_excel)  
#             table = new_excel.sheets()[0] 
# #             ws = new_excel.get_sheet(0)
#             excelRow = table.nrows
            return nrows
        
        else:
            return 0
            
        
        
  
# 抓取说说极评论数据
    def shuoshuoSpider(self,qq,cookie,referer,userAgent):

        pageIndex = 0

        myDarlingData = []


        bUrl = 'https://user.qzone.qq.com/proxy/domain/taotao.qq.com/cgi-bin/emotion_cgi_msglist_v6?uin='+qq+'&ftype=0&sort=0&pos='

        aUrl = 'g_tk=205161311&callback=_preloadCallback&code_version=1&format=jsonp&need_private_comment=1&qzonetoken=ea9ba2eece47b377dfb3dc8257345a76bdd421f842230f6ff03f8f7b0bd769bc6a54d2e39a755e66&g_tk=205161311'

        url = bUrl + str(pageIndex) + aUrl
        
        print url

        responseData = self.responseData('shuoshuo', url, cookie, referer, userAgent)
        startIndex = self.excelRowCount('说说.xls')
        
        if responseData.has_key('total'):

            totalNum = responseData['total']
            print startIndex
            print totalNum
            
            totalNum = totalNum - startIndex
            print totalNum
            pageCount = responseData['num']

            totalPageCount = totalNum/pageCount + 1
            totalPageCount = 1
            print totalPageCount
            
            for i in range(totalPageCount):

                responseData = self.responseData('shuoshuo', url, cookie, referer, userAgent)  
                url = bUrl + str(pageIndex) + aUrl
                pageIndex +=pageCount
                if responseData.has_key('msglist'):
                    count = len(responseData['msglist'])
                    for j in range(count):
                       
                        mInfo = responseData['msglist'][j]
                        content =  mInfo['content']
                        createTime = mInfo['createTime']

                        if mInfo.has_key('commentlist'):
                            
                            commentList = mInfo['commentlist']
                            commentCount = len(commentList)
                            commentArray = []
                            for c in range(commentCount):
                                commentString = ''
                                cInfo = commentList[c]
                                commentString = self.commentStringFromDic(cInfo, mInfo['name'])
                                commentArray.append(commentString)
                            tInfo = SSInfo(content,createTime,commentArray)
                            
                            myDarlingData.append(tInfo)

                        else:

                            commentArray = []
                            tInfo = SSInfo(content,createTime,commentArray)
                            myDarlingData.append(tInfo)

                        

        dataArrayCount = len(myDarlingData)
        
#         if startIndex == 0:
                    
        filename=xlwt.Workbook()
        sheet=filename.add_sheet("my_sheet",cell_overwrite_ok=True)
        sheet.write(startIndex,2,'start place',self.excelStyle())
        
        for row in range(0,dataArrayCount):

            cInfo = myDarlingData[row]

            commentArray = cInfo.commentArray

            commentCount = len(commentArray)

            print '..............'+str(commentCount)

            sheet.write(startIndex+row,0,cInfo.createTime)

            sheet.write(startIndex+row,1,cInfo.content)
            

            for ct in range(commentCount):
                cString = commentArray[ct]
                sheet.write(row,ct+2,cString)

        filename.save("/Users/docker/Desktop/说说.xls")

        


    
   

    def commentStringFromDic(self,commentDic,tName):

        commentString=''

        name = commentDic['name']

        commentString +=name

        commentString+='->'

        commentString+=tName+':'

        nContent = commentDic['content']

        commentString +=nContent

        if commentDic.has_key('list_3'):

            subCommentList = commentDic['list_3']

            subCount = len(subCommentList)

            for cc in range(subCount):

                commentString+='###'

                ccInfo = subCommentList[cc]

                cName = ccInfo['name']

                cContentStr = ccInfo['content']

                identity = '}'

                if identity in cContentStr:

                    nPos = cContentStr.index(identity)

                    cContent = cContentStr[nPos+1:-1]

                    myItems = re.findall('.*?{(.*?)}.*?',cContentStr,re.S)

                    cItems = myItems[0]

                    cArrayItems = cItems.split(',')

                    ccItems = cArrayItems[1]

                    ccArrayItems = ccItems.split(':')

                    ttName = ccArrayItems[1]

                    commentString +=cName

                    commentString+='->'

                    commentString+=ttName+':'

                    commentString+=cContent

        return commentString

        

blogDirAgent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1883.0 Safari/537.36'

blogDirReferer = 'http://user.qzone.qq.com/1239806145/2'

blogDirCookie = 'RK=t8XayzQIXX; pgv_pvid=152078441; __Q_w_s_hat_seed=1; __Q_w_s__QZN_TodoMsgCnt=1; cpu_performance_v8=1; randomSeed=294567; pt2gguin=o1239806145; uin=o1239806145; skey=@IdADXRJUm; ptisp=cnc; qzone_check=1239806145_1428222610; ptcz=e0f5a87ab81aee4eb33b0292f9f1073f5baae74e78481bc204765bb7b06de2b6; p_skey=dm*wDWxcKBA5hEnRzBIy3yLMwiZ0CdDtvWiS3ok*6LA_; pt4_token=i4uEhGxzzMhnAXbQ9Z2Lbw__; qz_screen=1440x900; pgv_info=ssid=s3073994260; QZ_FE_WEBP_SUPPORT=1; blabla=dynamic; Loading=Yes; qzspeedup=sdch'







blogContentAgent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1883.0 Safari/537.36'

blogContentReferer = 'http://cnc.qzs.qq.com/qzone/app/blog/v6/bloglist.html'

blogContentCookie = 'RK=t8XayzQIXX; pgv_pvid=152078441; __Q_w_s_hat_seed=1; __Q_w_s__QZN_TodoMsgCnt=1; randomSeed=294567; __Q_w_s__appDataSeed=1; scstat=5; pgv_info=ssid=s9796034864; qqmusic_uin=; qqmusic_key=; qqmusic_fromtag=; qzmusicplayer=qzone_player_285870766_1428299545752; rv2=80DB2A1ED1A8EA5176AB0D5B268418963F571D77AA0A7BA6FF; property20=D65DE6A83CED663FD0E8BE8F7B955C3DB236536CC6C1439C1392072F7240DF2C368E3D29D8DA2BE2; Loading=Yes; qz_screen=1440x900; QZ_FE_WEBP_SUPPORT=1; cpu_performance_v8=1; ptisp=cnc; ptcz=e0f5a87ab81aee4eb33b0292f9f1073f5baae74e78481bc204765bb7b06de2b6; pt2gguin=o1239806145; uin=o1239806145; skey=@u7FrgyeF2; p_uin=o1239806145; p_skey=2gSuGCS*ztnrSw5aCMCpf80HV5GmvcXZ3IP6*rcc-XM_; pt4_token=hjkiOfsnxV7K07nzVPjV6A__; qzone_check=1239806145_1428314835; qzspeedup=sdch; blabla=dynamic'



shuoshuoAgent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'

shuoshuoReferer = 'https://user.qzone.qq.com/1239806145/311'

# shuoshuoCookie = 'RK=t8XayzQIXX; pgv_pvid=152078441; pgv_info=ssid=s9796034864; pt2gguin=o1239806145; uin=o1239806145; skey=@u7FrgyeF2; ptisp=cnc; qzone_check=1239806145_1428282871; ptcz=e0f5a87ab81aee4eb33b0292f9f1073f5baae74e78481bc204765bb7b06de2b6'

shuoshuoCookie = 'pgv_pvi=8599567360; pgv_si=s7142751232; __Q_w_s__QZN_TodoMsgCnt=1; pt2gguin=o1239806145; ptisp=cnc; RK=E9TQiRQQVV; ptcz=5f4edae9fa07b27fb252d231fd0b88d133f87888a6522c7b6e0532e13f4e69d0; zzpaneluin=; zzpanelkey=; pgv_pvid=1413511842; pgv_info=ssid=s2935398492; ptui_loginuin=1239806145@qq.com; qz_screen=1440x900; o_cookie=1239806145; QZ_FE_WEBP_SUPPORT=1; __Q_w_s_hat_seed=1; uin=o1239806145; p_uin=o1239806145; tvfe_boss_uuid=3ec50c85708b6219; mobileUV=1_1611d8fdf98_1c44a; pac_uid=1_1239806145; qm_authimgs_id=3; qm_verifyimagesession=h01602692601c41dd87c6e8fb3bd93b3b7273e1470104f5e2f91a90bf41448846ab9baa49f0404c2948; skey=@uz8E4CLVY; Loading=Yes; __layoutStat=29; scstat=29; rv2=80A96066E9B83588C133B1682DE426DC0E4D28BB3BBC4B2507; property20=654E02D3802C2DCB62DD2A96D77A439917E5CF65654DB257C8DE8CD6B940F515FB90CE55768AD1C8; pt4_token=QSQQC-77q5wGjdPFyHFfHXM0QjK8Nvewu9D*ofm3*Mo_; p_skey=RLjtcpJLvfRdVrHdy02iRhqDz8e3j1ebSjfmofnF5Lw_; cpu_performance_v8=1; randomSeed=358572'

albumDirCookie = 'RK=t8XayzQIXX; pgv_pvid=152078441; pgv_info=ssid=s9796034864; qqmusic_uin=; qqmusic_key=; qqmusic_fromtag=; rv2=80DB2A1ED1A8EA5176AB0D5B268418963F571D77AA0A7BA6FF; property20=D65DE6A83CED663FD0E8BE8F7B955C3DB236536CC6C1439C1392072F7240DF2C368E3D29D8DA2BE2; pt2gguin=o1239806145; uin=o1239806145; skey=@u7FrgyeF2; ptisp=cnc; qzone_check=1239806145_1428315954; ptcz=e0f5a87ab81aee4eb33b0292f9f1073f5baae74e78481bc204765bb7b06de2b6'

albumDirAgent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1883.0 Safari/537.36'

albumDirReferer = 'http://cnc.qzs.qq.com/qzone/photo/v7/page/photo.html?init=photo.v7/module/albumList/index&navBar=1'



albumAgent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1883.0 Safari/537.36'

albumReferer = 'http://user.qzone.qq.com/1239806145/2'

albumCookie = 'RK=t8XayzQIXX; pgv_pvid=152078441; pgv_info=ssid=s3073994260; rv2=8082E953C1DA8771A364A6459C62FAA579DD2120C46BCB6FA1; property20=3C5726D9679BFA795C582EEFC81B8522D248A5158D54C28CD005704F5905E3F94A1B81639CD0EE40; pt2gguin=o1239806145; uin=o1239806145; skey=@IdADXRJUm; ptisp=cnc; qzone_check=1239806145_1428243129; ptcz=e0f5a87ab81aee4eb33b0292f9f1073f5baae74e78481bc204765bb7b06de2b6'



fBlogDirReferer = 'http://user.qzone.qq.com/2595127668?ptlang=1033'

fBlogDirCookie = 'RK=t8XayzQIXX; pgv_pvid=152078441; __Q_w_s_hat_seed=1; __Q_w_s__QZN_TodoMsgCnt=1; randomSeed=294567; __Q_w_s__appDataSeed=1; scstat=5; pgv_info=ssid=s9796034864; qqmusic_uin=; qqmusic_key=; qqmusic_fromtag=; qzmusicplayer=qzone_player_285870766_1428299545752; rv2=80DB2A1ED1A8EA5176AB0D5B268418963F571D77AA0A7BA6FF; property20=D65DE6A83CED663FD0E8BE8F7B955C3DB236536CC6C1439C1392072F7240DF2C368E3D29D8DA2BE2; Loading=Yes; qz_screen=1440x900; QZ_FE_WEBP_SUPPORT=1; cpu_performance_v8=1; ptisp=cnc; ptcz=e0f5a87ab81aee4eb33b0292f9f1073f5baae74e78481bc204765bb7b06de2b6; pt2gguin=o1239806145; uin=o1239806145; skey=@u7FrgyeF2; p_uin=o1239806145; p_skey=2gSuGCS*ztnrSw5aCMCpf80HV5GmvcXZ3IP6*rcc-XM_; pt4_token=hjkiOfsnxV7K07nzVPjV6A__; qzone_check=1239806145_1428314835; qzspeedup=sdch; blabla=dynamic'



fAlbumDirReferer = 'http://user.qzone.qq.com/2595127668/4'

fAlbumDirCookie = 'RK=t8XayzQIXX; pgv_pvid=152078441; __Q_w_s_hat_seed=1; __Q_w_s__QZN_TodoMsgCnt=1; randomSeed=294567; __Q_w_s__appDataSeed=1; scstat=5; pgv_info=ssid=s9796034864; p_uin=o1239806145; rv2=8034A546C2D678980B80A86A27D1424D95B3563E3417EFF9D7; property20=953473A3E3CA87DB1E8C918E8152D3E311BBA7CCC7B2F0FE42720E75B72B3D5B060116535B112F97; qqmusic_uin=; qqmusic_key=; qqmusic_fromtag=; qzmusicplayer=qzone_player_393432424_1428321309803; pt2gguin=o1239806145; uin=o1239806145; skey=@u7FrgyeF2; ptisp=cnc; qzone_check=1239806145_1428323873; ptcz=e0f5a87ab81aee4eb33b0292f9f1073f5baae74e78481bc204765bb7b06de2b6; Loading=Yes; qzspeedup=sdch; p_skey=Arzcwk4LLi-C5hZ1YKonHCOQV4xAwV*Ex3*YCDES-ak_; pt4_token=4cqzMhPUSi4JEcQxMq4P-A__; qz_screen=1440x900; QZ_FE_WEBP_SUPPORT=1; cpu_performance_v8=1; blabla=dynamic'

fAlbumDirAgent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1883.0 Safari/537.36'

   

fAlbumCookie = 'RK=t8XayzQIXX; pgv_pvid=152078441; __Q_w_s_hat_seed=1; __Q_w_s__QZN_TodoMsgCnt=1; randomSeed=294567; __Q_w_s__appDataSeed=1; scstat=5; pgv_info=ssid=s9796034864; p_uin=o1239806145; rv2=8034A546C2D678980B80A86A27D1424D95B3563E3417EFF9D7; property20=953473A3E3CA87DB1E8C918E8152D3E311BBA7CCC7B2F0FE42720E75B72B3D5B060116535B112F97; qqmusic_uin=; qqmusic_key=; qqmusic_fromtag=; qzmusicplayer=qzone_player_393432424_1428321309803; pt2gguin=o1239806145; uin=o1239806145; skey=@u7FrgyeF2; ptisp=cnc; qzone_check=1239806145_1428323873; ptcz=e0f5a87ab81aee4eb33b0292f9f1073f5baae74e78481bc204765bb7b06de2b6; Loading=Yes; qzspeedup=sdch; p_skey=Arzcwk4LLi-C5hZ1YKonHCOQV4xAwV*Ex3*YCDES-ak_; pt4_token=4cqzMhPUSi4JEcQxMq4P-A__; qz_screen=1440x900; QZ_FE_WEBP_SUPPORT=1; cpu_performance_v8=1; blabla=dynamic'

fAlbumReferer = 'http://user.qzone.qq.com/2595127668/4'





ps = QQSpider()




# 说说的抓取

ps.shuoshuoSpider('1239806145', shuoshuoCookie, shuoshuoReferer, shuoshuoAgent)



# 日志的抓取

# mBlogDirArray = ps.blogDirSpider('2595127668', fBlogDirCookie, fBlogDirReferer, blogDirAgent)   
# 
# ps.blogContentSpider(mBlogDirArray, '2595127668', blogContentCookie, blogContentReferer, blogContentAgent)



# 相册的抓取

# albumDirArray = ps.albumDirSpider('1239806145',albumDirCookie,albumDirReferer,albumDirAgent)
# 
# ps.albumSpider('1239806145', albumCookie, albumReferer, albumAgent,albumDirArray)