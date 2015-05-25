import tweepy
import sys
import os
import re

etc_dir = os.environ['HOME'] + "/etc/twerial"
prog_name = os.path.splitext(sys.argv[0])[0]

def read_options(rcfile):
    opts = { }
    fp = open(rcfile,'r')
    for txt in fp:
        m = re.match(r'^\s*(\w+)\s*=\s*(.*)\s*$',txt)
        if m:
            opts[m.group(1)] = m.group(2)
        elif re.match('r^\s*$',txt) or re.match('^\s*#',txt):
            pass
    fp.close()
    for f in ['counter_file', 'tweet_file', 'image_dir']:
        if not re.match(r'^/',opts[f]):
            opts[f] = etc_dir + '/' + opts[f]
    return opts

def read_counter(opts):
    fp = open(opts['counter_file'],'r')
    ctr = int(fp.readline())
    fp.close()
    return ctr

def inc_counter(opts):
    fp = open(opts['counter_file'],'r+')
    ctr = int(fp.readline())
    fp.seek(0)
    fp.write(str(ctr+1))
    fp.close()
    return

def read_tdata(opts,ctr):
    tdata = { 'lines' : [ ]}
    i = 0
    fp = open(opts['tweet_file'],'r')
    for txt in fp:
        if re.match(r'^\s*-*\s*$',txt):
            i += 1
        elif re.match(r'^\s*#',txt):
            pass
        elif i == ctr:
            m = re.match(r'^\s*\\(img|url)\s+(.*?)\s*$',txt)
            if m:
                k = m.group(1)
                v = m.group(2)
                if k == "img" and not re.match(r'^/',v):
                    v = opts['image_dir'] + '/' + v
                tdata[k] = v
            else:
                tdata['lines'].append(txt.rstrip())
        else:
            pass
    fp.close()
    return tdata

def get_api(opts):
    auth = tweepy.OAuthHandler(opts['app_key'], opts['app_secret'])
    auth.set_access_token(opts['oauth_token'], opts['oauth_secret'])
    return tweepy.API(auth)

def post_tweet(api,tdata):
    prev = None
    lines = tdata['lines']
    imgfile = tdata['img']
    for i, txt in enumerate(lines):
        if i == (len(lines) - 1) and imgfile:
            if prev:
                st = api.update_with_media(status = txt, \
                                           filename = imgfile, \
                                           in_reply_to_status_id = prev.id)
                prev = st
            else:
                prev = api.update_with_media(status = txt, \
                                            filename = imgfile)
        else:
            if prev:
                st = api.update_status(status = txt, \
                                       in_reply_to_status_id = prev.id)
                prev = st
            else:
                prev = api.update_status(status = txt)
    return

opts = read_options(etc_dir + "/" + prog_name + ".rc")

ctr = read_counter(opts)

tdata = read_tdata(opts,ctr)

api = get_api(opts)

post_tweet(api,tdata)

inc_counter(opts)
