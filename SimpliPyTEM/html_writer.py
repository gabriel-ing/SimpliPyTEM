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
    print(images)
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
            with a.ul(klass='Image_group'):
                for image in images:

                    print(image)
                    image_name = image.strip('.jpg').split('/')[-1].replace('_', ' ')
                    

    #                    with a.h3():
    #                        a(image.strip('.jpg').split('/')[-1].replace('_', ' '))
                    
                    with a.li():
                        with a.a(href=''):
                            a.img(src=image, alt=image_name)    
                            with a.p():
                                a(image_name)
                            a.img(src=image, alt=image_name, klass='preview')    
            if  videos:
                with a.div(klass='Videos'):
                    with a.h2():
                        a('Videos')
                    with a.ul(klass='Video_group'):
                        for video in videos:
                            with a.li():

                                with a.video('controls', width=600,height=600):
                                    a.source(src=video, type="video/mp4")
                                with a.p():
                                    a(video.strip('.mp4').split('/')[-1].replace('_',' '))

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
    else:
        video_files = []
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
*
{
    border: 0;
    margin: 0;
    padding: 0;
}

/* =Basic HTML, Non-essential
----------------------------------------------------------------------*/

a
{
    text-decoration: none;
}

body
{
    background: #151D35;
    color: #777;
    margin: 0 auto;
    padding: 50px;
    position: relative;
    width: 950px;
}

h1
{
    background: inherit;
    border-bottom: 2px dashed #ccc;
    color: #BB0E5F;
    font: 50px Georgia, serif;
    font-weight: 700;
    margin: 0 0 10px;
    padding: 0 0 5px;
    text-align: center;
}
h2{
    border-bottom: 1px dashed #ccc;
    color: #D8BBEA;
    font: 30px Georgia, serif;
    font-weight: 700;
    margin: 20 0 10px;
    padding: 0 0 5px;
    text-align: center;
}

p
{
    clear: both;
    font: 15px Verdana, sans-serif;
    padding: 15px 0;
    text-align: center;
    color:#BB0E5F;
}

p a
{
    background: inherit;
    color: #BB0E5F;
}

p a:hover
{
    background: inherit;
    color: #BB0E5F;
}

.Videos
{
    
        
    

}

/* =Hoverbox Code
----------------------------------------------------------------------*/

.Image_group
{
    cursor: default;
    list-style: none;
    
}

.Image_group a
{
    cursor: default;
}

.Image_group a .preview
{
    display: none;
}

.Image_group a:hover .preview
{
    display: block;
    position: absolute;
    top: -33px;
    left: -45px;
    z-index: 1;
}

.Image_group img
{
    background: #fff;
    border-color: #aaa #ccc #ddd #bbb;
    border-style: solid;
    border-width: 1px;
    color: inherit;
    padding: 2px;
    vertical-align: top;
    width: 250px;
    height: 250px;
}

.Image_group li
{
    background: #95A9C1;
    border-color: #95A9C1;
    border-style: solid;
    border-width: 1px;
    color: inherit;
    display: inline;
    float: left;
    width: 280;
    height: 300;
    margin: 3px;
    padding: 10px;
    position: relative;
}

.Image_group .preview
{
    border-color: #000;
    width: 600px;
    height: 600px;
}


.Video_group li{
    text-align: center;
    background: #95A9C1;
    border-color: #95A9C1;
    border-style: solid;
    border-width: 1px;
    color: inherit;
    display: inline;
    float: left;
    padding: 10px 10px 10px 10px;
    position: relative;
    margin: auto;

}

''')

if __name__=='__main__':
    directory = os.getcwd()
    title = input('Give a title for the experiment: ')
    title=title.replace(' ', '_')
    images, videos = get_files('Images', 'Videos')
    print(images)
    write_html(images, videos, title=title)
    write_css()
