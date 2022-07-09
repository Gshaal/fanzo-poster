import datetime

import arrow
from PIL import Image, ImageDraw, ImageFont
import imgkit
from html2image import Html2Image
import requests
import xmltodict
import jinja2
import os
from bs4 import BeautifulSoup as Soup, Tag


class FanzoPoster:
    def __init__(self):
        self.get_data()

        # create Image object
        self.text1 = 'Create Feature Image'
        self.text2 = 'With Python'
        self.img_name = 'featured-image-creation-with-python.png'
        self.color = 'dark_blue'  # grey,light_blue,blue,orange,purple,yellow,green
        self.font = 'Roboto-Bold.ttf'

        self.background = Image.open('default.jpg')
        self.foreground = Image.open('out.png')

        # create the coloured overlays
        self.colors = {
            'dark_blue': {'c': (27, 53, 81), 'p_font': 'rgb(255,255,255)', 's_font': 'rgb(255, 212, 55)'},
            'grey': {'c': (70, 86, 95), 'p_font': 'rgb(255,255,255)', 's_font': 'rgb(93,188,210)'},
            'light_blue': {'c': (93, 188, 210), 'p_font': 'rgb(27,53,81)', 's_font': 'rgb(255,255,255)'},
            'blue': {'c': (23, 114, 237), 'p_font': 'rgb(255,255,255)', 's_font': 'rgb(255, 255, 255)'},
            'orange': {'c': (242, 174, 100), 'p_font': 'rgb(0,0,0)', 's_font': 'rgb(0,0,0)'},
            'purple': {'c': (114, 88, 136), 'p_font': 'rgb(255,255,255)', 's_font': 'rgb(255, 212, 55)'},
            'red': {'c': (255, 0, 0), 'p_font': 'rgb(0,0,0)', 's_font': 'rgb(0,0,0)'},
            'yellow': {'c': (255, 255, 0), 'p_font': 'rgb(0,0,0)', 's_font': 'rgb(27,53,81)'},
            'yellow_green': {'c': (232, 240, 165), 'p_font': 'rgb(0,0,0)', 's_font': 'rgb(0,0,0)'},
            'green': {'c': (65, 162, 77), 'p_font': 'rgb(217, 210, 192)', 's_font': 'rgb(0, 0, 0)'}
        }
        self.template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        self.jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(self.template_dir),
                                            autoescape=True)

    def add_text(self, img, color, text1, text2, logo=False, font='Roboto-Bold.ttf', font_size=75):
        draw = ImageDraw.Draw(img)
        p_font = color['p_font']
        s_font = color['s_font']
        # starting position of the message
        img_w, img_h = img.size
        height = img_h // 3
        font = ImageFont.truetype(font, size=font_size)
        if logo == False:
            print("empty")
        else:
            text1_offset = (img_w // 4, height)
            text2_offset = (img_w // 4, height + img_h // 5)
            draw.text(text1_offset, text1, fill=p_font, font=font)
            draw.text(text2_offset, text2, fill=s_font, font=font)
        return img

    def add_logo(self, background, foreground):
        bg_w, bg_h = background.size
        img_w, img_h = foreground.size
        print(bg_h - img_h)
        img_offset = (30, 1500 // 2)
        background.paste(foreground, img_offset, foreground)
        return background

    def write_image(self, background, color, text1, text2, foreground=''):
        if not foreground:
            self.add_text(background, color, text1, text2)
        else:
            self.add_logo(background, foreground)
        return background

    def get_data(self):
        data = requests.get('https://www-service.fanzo.com/venues/19415/fixture/xml?newFields=1')
        dict_data = xmltodict.parse(data.content)
        content = self.populate_html(dict_data['rss']['channel'])
        print(content)
        hti = Html2Image()
        with open('./Template.html') as f:
            file = Soup(f.read(), 'html.parser')
            file.find('table').insert(1, content)

        with open('./out.html', 'w') as f2:
            f2.write(file.prettify())


        with open('./out.html') as f3:
            hti.screenshot(f3.read(), save_as='out.png', size=(1000, 1200))


    def populate_html(self, data):
        html = ''
        with open('./Template.html') as f:
            file = Soup(f.read(), 'html.parser')
            tbody = file.new_tag("tbody")
        for key, value in data.items():
            for match in value:
                tr1 = file.new_tag("tr")
                tbody.append(tr1)

                th = file.new_tag("th", attrs={"class": "tg-cw9i", "colspan" : "3"})
                th.string = arrow.get(match['startTimeLocal']).format("dddd Do MMM")
                tr1.append(th)

                tr2 = file.new_tag("tr")
                tbody.append(tr2)

                td1 = file.new_tag("td", attrs={"class": "tg-a7sn"})
                td1.string = arrow.get(match['startTimeLocal']).format("H:mm")

                td2 = file.new_tag("td", attrs={"class": "tg-a7sn"})
                td2.string = match['title']

                td3 = file.new_tag("td", attrs={"class": "tg-a7sn"})
                td3.string = match['sport']

                tr2.append(td1)
                tr2.append(td2)
                tr2.append(td3)

                # html += '<tr>'
                # html += '<th class="tg-cw9i" colspan="3">{}/th>'.format(match['startTimeLocal'])
                # html += '</tr>'
                # html += '<tr>'
                # html += '<td class="tg-a7sn"> {} </td>'.format(match['startTimeLocal'])
                # html += '<td class="tg-a7sn"> {} </td>'.format(match['title'])
                # html += '</tr>'
        return tbody

    def run(self):
        t1 = self.write_image(self.background, self.colors[self.color], self.text1, self.text2,
                              foreground=self.foreground)
        t1.save(self.img_name)


writer = FanzoPoster()
writer.run()
