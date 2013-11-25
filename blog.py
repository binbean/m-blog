#!/usr/bin/env python
# encoding: utf-8

import codecs
import markdown
import PyRSS2Gen
import flask

import os, sys, datetime, re
#import pdb
#import hashlib, base64
#from Crypto.Cipher import AES

reload(sys)
sys.setdefaultencoding('utf-8')

# configuration
POST_DIR = os.getcwd() + os.sep + 'posts'
TITLE = 'Blog of binbean!'
URL = 'binbean.github.io'

app = flask.Flask(__name__)
app.config.from_object(__name__)

pattern_title = re.compile(r'(^title[\s]*:[\s]*)(.+)')
pattern_date = re.compile(r'(^date[\s]*:[\s]*)(.+)')
pattern_categories = re.compile(r'(^categories[\s]*:[\s]*)(.+)')

def file_read(file_path):
    f = codecs.open(file_path, mode='r', encoding='utf8')
    lines = []
    try:
        lines = f.readlines()
    except:
        pass
    finally:
        f.close()
    return lines

def file_handler(file_path):
    lines = file_read(file_path)
    index = 1
    for line in lines[1:]:
        index += 1
        if pattern_title.match(line):
            title = pattern_title.match(line).groups()[1]
        elif pattern_date.match(line):
            date = pattern_date.match(line).groups()[1]
        #if line.find('title:') == 0:
        #    title = line.replace('title: "', '')[0:-2]
        #elif line.find('date:') == 0:
        #    date = line.replace('date: ', '')[0:-1]
        elif line.find('---') == 0:
            break
    post = {}
    content = u''.join(lines[index:])
    #for line in lines[index:]:
    #    content += line
    post['title'] = title
    post['date'] = date
    post['content'] = markdown.markdown(content)

    post['name'] = file_path.split(os.sep)[-1].split('.')[0]
    return post

def post_handler():
    post_dir = app.config['POST_DIR']
    files = os.listdir(post_dir)
    file_list = [post_dir + os.sep + f for f in files]
    file_list.sort(reverse=True)
    return file_list
    #for f in files:
    #    file_list.append(post_dir + os.sep + f)
    #    file_list.sort(reverse=True)
    #return file_list;

def category_count():
    categories = []
    category_count = {}
    for file in post_handler():
        lines = file_read(file)
        for line in lines[1:]:
            if pattern_categories.match(line):
                tags = pattern_categories.match(line).groups()[1]
                for tag in tags.split(','):
                    categories.append(tag.strip())
                break
    categories.sort()
    for category in categories:
        category_count[category] = category_count.get(category, 0) + 1
    return category_count

def post_list(file_list):
    return [file_handler(file) for file in file_list if file_handler(file)]
    #posts = []
    #for file in file_list:
    #    article = file_handler(file)
    #    if article:
    #        posts.append(article)
    #return posts

def rss_maker():
    file_list = post_handler()
    posts = post_list(file_list)
    rss_items = []
    for post in posts:
        link = app.config['URL'] + '/article/' + post['name']
        rss_item = PyRSS2Gen.RSSItem(
                title = post['title'],
                link = link,
                description = post['content'],
                pubDate = datetime.datetime(
                    int(post['date'][0:4]),
                    int(post['date'][5:7]),
                    int(post['date'][8:10])
                    )
                )
        rss_items.append(rss_item)
        rss = PyRSS2Gen.RSS2(
            title = app.config['TITLE'],
            link = app.config['URL'],
            description = '',
            lastBuildDate = datetime.datetime.utcnow(),
            items = rss_items)
        rss.write_xml(open('rss.xml', 'w'), encoding = 'utf-8')

def render_articles(template, file_list, page, file_count, category = ''):
    posts = post_list(file_list[page:page+3])
    categories = category_count()
    prev = True if page > 2 else False
    pnext = True if page + 4 <= file_count else False
    prevnum = page - 3 if page > 3 else 0
    return flask.render_template(template, title = app.config['TITLE'], url = app.config['URL'],
            articles = posts, categories = categories, category = category,
            prev = prev, pnext = pnext,
            prevnum = prevnum, nextnum = page + 3)


@app.route('/')
@app.route('/<int:page>')
@app.route('/index/<int:page>')
def index(page = 0):
    file_list = post_handler()
    return render_articles('index.html', file_list, page, len(file_list))
 
@app.route('/article/<name>')
def article(name):
    post_path = app.config['POST_DIR'] + os.sep + name.replace('.', '') + '.md'
    article = file_handler(post_path)
    categories = category_count()
    return flask.render_template('post.html', title = app.config['TITLE'],
            url = app.config['URL'], article = article, categories = categories)

@app.route('/category/<string:category>')
@app.route('/category/<string:category>/<int:page>')
def category(category, page = 0):
    tag_files = []
    for file in post_handler():
        lines = file_read(file)
        for line in lines[1:]:
            if pattern_categories.match(line):
                tags = pattern_categories.match(line).groups()[1]
                if tags.find(category) != -1:
                    tag_files.append(file)
                break
    return render_articles('category.html', tag_files, page, len(tag_files), category)

@app.route('/rss.xml')
def rss():
    f = open('rss.xml', 'r')
    return flask.Response(f.read(), mimetype = 'application/rss+xml')

@app.errorhandler(404)
def not_found(error):
    return flask.render_template('404.html'), 404

if __name__ == '__main__':
    rss_maker()
    app.run(debug=True)
