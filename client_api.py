from flask import Flask
from flask_restful import reqparse, Api, Resource
from twitterscraper import query_tweets
from twitterscraper.query import query_tweets_from_user

DEFAULT_PAGES_LIMIT = 40

app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('pages_limit', type=int)


def _transform_to_json(tweet):
    return {
        'account': {
            'fullname': tweet.fullname,
            'href': '/' + tweet.user,
            'id': tweet.id
        },
        'date': tweet.timestamp.strftime(
            '%I:%M %p - %d %b %Y'
        ).lstrip('0').replace(' 0', ' '),
        'hashtags': [
            tag for tag in tweet.text.split() if tag[0] == '#'
        ],
        'likes': tweet.likes,
        'replies': tweet.replies,
        'retweets': tweet.retweets,
        'text': tweet.text
    }


class HashTagsApi(Resource):
    """Get tweets by a hashtag. Get the list of tweets with the given hashtag.
    :param pages_limit: integer, specifies the number of pages to retrieve.

    Example request:

    curl -H "Accept: application/json" -H "Content-Type: application/json" -X \
    GET http://localhost:xxxx/hashtags/Python?pages_limit=3

    Example response:

    [{"account": {"fullname": "Raymond Hettinger",
                  "href": "/raymondh",
                  "id": 14159138},
      "date": "12:57 PM - 7 Mar 2018",
      "hashtags": ["#python"],
      "likes": 169,
      "replies": 13,
      "retweets": 27,
      "text": "Historically, bash filename pattern matching was known
               as \"globbing\".  Hence, the #python module
               called \"glob\".\n\n
               >>> print(glob.glob('*.py')\n\n
               If the function were being added today, it would probably
               be called os.path.expand_wildcards('*.py') which would be
               less arcane."},
      ...
    ]
    """
    def get(self, hashtag):
        args = parser.parse_args()
        pages_limit = args.get('pages_limit', DEFAULT_PAGES_LIMIT)
        list_of_tweets = [
            _transform_to_json(tweet) for tweet in query_tweets(
                query='#'+hashtag,
                limit=pages_limit
            )[:pages_limit]
        ]

        return [list_of_tweets]


class UserTweetsApi(Resource):
    """Get the list of tweets that user has on his feed in json format.
    :param pages_limit: integer, specifies the number of pages to retrieve.

    Example request:

    curl -H "Accept: application/json" -H "Content-Type: application/json" -X \
    GET http://localhost:xxxx/users/Twitter?pages_limit=3

    Example response:


    [{"account": {"fullname": "Twitter",
                  "href": "/Twitter",
                  "id": 783214},
      "date": "2:54 PM - 8 Mar 2018",
      "hashtags": ["#InternationalWomensDay"],
      "likes": 287,
      "replies": 17,
      "retweets": 70,
      "text": "Powerful voices. Inspiring women.\n\n#InternationalWomensDay
               https://twitter.com/i/moments/971870564246634496"},
       ...
    ]
    """
    def get(self, user):
        args = parser.parse_args()
        pages_limit = args.get('pages_limit', DEFAULT_PAGES_LIMIT)
        list_of_tweets = [
            _transform_to_json(tweet) for tweet in query_tweets_from_user(
                user=user,
                limit=pages_limit
            )[:pages_limit]
        ]

        return [list_of_tweets]


class HelpApi(Resource):
    def get(self):
        return {'message': 'Please, read a documentation for API'}


api.add_resource(
    HashTagsApi,
    '/hashtags/<string:hashtag>',
    endpoint='hashtags'
)

api.add_resource(
    UserTweetsApi,
    '/users/<string:user>',
    endpoint='users'
)

api.add_resource(HelpApi, '/')

if __name__ == '__main__':
    app.run(debug=True)