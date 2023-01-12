from airium import Airium
import os

def write_html(images, videos, title='Default_experiment_title', notes='', **kwargs):
    '''
    Writes html file containing the images and videos from an experiment so they can be viewed on a webbrowser. This can be preferable over PDFS as the videos can be played. 
    The images and videos are only linked in this html, so in order to share the page these need to be sent as well. 

    Parameters
    ----------
        Images:list
            List of images (including their path from the current directory), can be made with get_files()

        Videos: list
            List of videos (including their path from the current directory), can be made with get_files()
        
        Title:str
            The title for the experiment (name of html doc and title of the resulting page)
    
        Notes:str
            Accompanying notes for the experiment, included at the top of the doc.

    Output
    ------
        HTML document {title}.html saved in the current working directory. This html document has the images from an experiment as well as playable videos.
    '''

    a =Airium()
    with a.html(lang='en'):
        with a.head():
            a.meta(charset='utf-8', content='width=device-width')
            a.title(_t='')
            a.link(href="style.css", rel='stylesheet', type='text/css')
        with a.body():
            with a.div(klass='banner'):
                with a.h1():
                    if title:
                        a(title.replace('_', ' ').strip('.html'))
                with a.h3():
                    a(notes)
            with a.h2():
                a('Images')
            for image in images:
                with a.div(klass='Image_group'):

                    with a.h3():
                        a(image.strip('.jpg').split('/')[-1].replace('_', ' '))
                    a.img(src=image, alt='Alt text')    
            with a.h2():
                a('Videos')
            for video in videos:
                with a.div(klass='Video_group'):
                    with a.h3():
                        a(video.strip('.mp4').split('/')[-1].replace('_',' '))
                    with a.video('controls', width=500,height=460):
                        a.source(src=video, type="video/mp4")


        if 'outdir' in kwargs:
            outdir = kwargs['outdir']
            title = outdir + '/' + title
        title+='.html'


    with open(title, 'w') as f:
        f.write(str(a))        



def get_files( imagedir, videodir=None, image_pattern='', video_pattern=''):
    '''
    Simple method for getting the image and video files. 

    Parameters
    ----------

        imagedir:str
            Directory containing the images (jpg, png or tif format)
        videodir:str
            Directory containing videos. Videos must  be .mp4
        image_pattern:str
            Pattern which the images contain, it is assumed they will be .jpg but if any more specific patterns in the filename are required (E.g. to  only include a single sample) It can be added here. 
        video_pattern:str
            As image pattern but for videos. 
        
    '''
    #current_dir = os.getcwd()
    #os.chdir(directory) 
    image_files = [imagedir+'/'+x for x in os.listdir(imagedir) if x[-3:]=='jpg' or x[-3:]=='tif' or x[-3:]=='png' and image_pattern in x]
    #print(image_files)
    if videodir and videodir in os.listdir('.'):
        video_files = [videodir+'/'+x for x in os.listdir(videodir) if x[-3:]=='mp4' and video_pattern in x]
    #print(video_files)
    #os.chdir(current_dir)
    return image_files, video_files




def write_css(outdir=None):
    '''
    Writes a basic css document called style.css, this is linked in the html generated. This gives it some basic formatting. You may consider making your own css for better formatting. 

    '''

    if outdir:
        cssname = outdir+'/style.css'
    else:
        cssname='style.css' 
    with open(cssname, 'w') as f:
        f.write('''
* {
    font-family: Helvetica;
}
html{
    background-color: black;
}
h1{
    font-size: 80px;
    font-weight:bold;
    text-justify: center;
}
.banner{
    background-color:#D8BBEA;
    width:100%;
    top:0px;
    left:0px;
    height:200px;


}
h2{
    text-align:center;
    padding: 10px 10px;
    font-size:40px;
    width: 150px;
    margin:20px auto 20px auto;
    background-color: #95A9C1;
}

img{
    border:black 3px solid;
    display:inline-block;
    /*flex: 0 1 auto;*/
    justify-content: center;
    width:97%;
    margin:10px 10px 10px 10px;


}
h3{
    text-align:center;
}
.Image_group{
    background-color: rgb(200, 200, 200);
    padding:10px 10px 10px 10px;
    margin: 0px 0px 10px 0px;
    width:97%;
    display:inline-block;
    align-items: center;
}
video{
    margin:auto;
    width:90%;
    align-items: center;
    justify-content: center;
}
.Video_group{
    margin:auto;
    background-color:rgb(200, 200, 200) ;
    display: inline-block;
    align-items: center;
    padding:10px 10px 10px 10px;
    margin: 0px 0px 10px 0px;
    width:97%
})
''')



if __name__=='__main__':
    directory = os.getcwd()
    title = input('Give a title for the experiment: ')
    title=title.replace(' ', '_')
    images, videos = get_files(directory, 'Images', 'Videos')
    write_html(images, videos, title=title)
    write_css()
