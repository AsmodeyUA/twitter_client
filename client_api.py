from flask import Flask
from flask_restful import reqparse, abort, Api, Resource
from twitterscraper import query_tweets

DEFAULT_PAGES_LIMIT = 40

app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('pages_limit', type=int)


def transform_to_json(tweet):

    return {
        'account': {
            'fullname': tweet.fullname,
            'href': '/' + tweet.user,
            'id': tweet.id
        },
        'date': tweet.timestamp.strftime(
            '%I:%M %p - %d %b %Y'
        ).lstrip('0').replace(' 0', ' '),

        # 'hashtags': ["#python"],
        'likes': tweet.likes,
        'replies': tweet.replies,
        'retweets': tweet.retweets,
        'text': tweet.text
    }


class HashTagsApi(Resource):
    def get(self, hashtag):
        args = parser.parse_args()
        pages_limit = args.get('pages_limit', DEFAULT_PAGES_LIMIT)
        list_of_tweets = [
            transform_to_json(tweet) for tweet in query_tweets(hashtag, limit=pages_limit)[:pages_limit]
        ]

        return {
            'hashtag': hashtag,
            'pages_limit': pages_limit,
            'tweets': list_of_tweets
        }


class HelpApi(Resource):
    def get(self):
        return {'message': 'Please, read a documentation for API'}


api.add_resource(
    HashTagsApi,
    '/hashtags/<string:hashtag>',
    endpoint = 'hashtags'
)

api.add_resource(HelpApi, '/')

if __name__ == '__main__':
    app.run(debug=True)