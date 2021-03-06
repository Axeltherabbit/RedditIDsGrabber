import praw
import prawcore
import argparse
import time

from functools import wraps
from socket import error as SocketError


# original source https://github.com/renfredxh/compilebot/blob/master/compilebot/compilebot.py
def handle_api_exceptions(max_attempts=1):
    """Return a function decorator that wraps a given function in a
    try-except block that will handle various exceptions that may
    occur during an API request to reddit. A maximum number of retry
    attempts may be specified.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_attempts:
                sleep_time = None
                error_msg = ""
                try:
                    return func(*args, **kwargs)
                # Handle and log miscellaneous API exceptions
                except praw.exceptions.ClientException as e:
                    error_msg = 'Client Exception "{error}" occurred: '.format(error=e)
                except praw.exceptions.APIException as e:
                    # this is ugly as fuck but should work
                    e = str(e)
                    if e.startswith("RATELIMIT:"):
                        sleep_time = int("".join(c for c in e if c.isdigit())) * 60 + 1
                    error_msg = 'API Exception "{error}" occurred: '.format(error=e)
                except SocketError as e:
                    error_msg = 'SocketError "{error}" occurred: '.format(error=e)
                    print(error_msg)
                except praw.exceptions.PRAWException as e:
                    error_msg = 'PRAW Exception "{error}" occurred: '.format(error=e)
                sleep_time = sleep_time or retries * 150

                print(
                    "{0} in {f}. Sleeping for {t} seconds. "
                    "Attempt {rt} of {at}.".format(
                        error_msg,
                        f=func.__name__,
                        t=sleep_time,
                        rt=retries + 1,
                        at=max_attempts,
                    )
                )
                time.sleep(sleep_time)
                retries += 1

        return wrapper

    return decorator


def get_last_id(reddit):
    " return the last ID posted on /r/all"
    last_id = None
    while not last_id:
        try:
            last_id = int(reddit.subreddit("all").new(limit=1)[0], 36)
        except:
            continue
    return last_id


def readwords():
    " return a list of word from the file wlist.txt "
    with open("wlist.txt", "r") as f:
        return f.read().split()


def removeolds(l: list, last_id: str):
    "removes old IDs from the list"
    pos = len(l) // 2
    while True:
        if int(l[pos], 36) >= last_id:
            if int(l[pos - 1], 36) < last_id:
                return l[pos:]
            else:
                pos -= pos // 2
                continue
        else:
            pos += pos // 2


def wait(reddit, target) -> None:
    """
    Hold the script and watch for the latest IDS untill it's close enough
    """
    sleep_time = 3
    while True:
        last_id = get_last_id(reddit)
        distance = int(target, 36) - last_id
        print("distance: ", distance)
        if distance <= 1000:
            sleep_time = 1
        if distance <= 200:
            return
        time.sleep(sleep_time)


def post(subreddit, title, flair_id, target) -> bool:
    """spams submission trying to get the target id"""
    while True:
        submited = submit(subreddit, flair_id, title)
        if submited.id.strip() != target:
            post_id = submited.id
            delete(submited)
            print("removed:", post_id)
            if int(post_id, 36) - int(target, 36) > 0:
                print("You missed", target)
                return False
        else:
            print("target", target, "taken")
            return True


@handle_api_exceptions(max_attempts=3)
def submit(subreddit, flair, title):
    " post submission function"
    return subreddit.submit(
        title=title,
        selftext="It's me a bot, don't ban me pls, I'll delete this post soon",
        flair_id=flair,
    )


@handle_api_exceptions(max_attempts=3)
def delete(submited):
    "delete a post"
    submited.delete()


def getID(target, reddit, subreddit, title, flair):
    " Wait untill it's close enough and then spams posts to get the ID"
    wait(reddit, target)
    subreddit = reddit.subreddit(subreddit)
    post(subreddit, title, flair, target)


def main(
    clientid: str,
    clientsecret: str,
    password: str,
    username: str,
    title: str,
    subreddit: str,
    target: str,
    flair: str,
) -> None:

    # set the default flair to None if not passed
    if not flair:
        flair = None
    if not target:
        target = None
    # read https://praw.readthedocs.io/en/latest/getting_started/authentication.html
    reddit = praw.Reddit(
        client_id=clientid,
        client_secret=clientsecret,
        password=password,
        user_agent=f"bot by /u/{username}",
        username=username,
    )
    reddit.validate_on_submit = True
    try:
        reddit.user.me()
    except prawcore.exceptions.OAuthException:
        print("Authentication failed")
        return

    if target:
        getID(target, reddit, subreddit, title, flair)
    else:
        l = removeolds(readwords(), get_last_id(reddit))
        for target in l:
            getID(target, reddit, subreddit, title, flair)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script to get redd.it/{IDS}")
    parser.add_argument(
        "--clientid",
        type=str,
        help=(
            "The client ID is the 14-character string listed just under “personal use"
            " script” for the desired https://www.reddit.com/prefs/apps/"
        ),
    )
    parser.add_argument(
        "--clientsecret",
        type=str,
        help=(
            "The client secret is the 27-character string listed adjacent to secret for"
            " the application."
        ),
    )
    parser.add_argument(
        "--password", type=str, help="Your pussyword",
    )
    parser.add_argument("--username", type=str, help="Your reddit username")
    parser.add_argument("--title", type=str, help="The post title (can not be edited)")
    parser.add_argument("--subreddit", type=str, help="Your subreddit target")
    parser.add_argument(
        "--target",
        type=str,
        help=(
            "The target ID if not target is specified will use a word list in the file"
            " wlist.txt"
        ),
    )
    parser.add_argument(
        "flairid",
        type=str,
        help="The flair id of the subreddit, leave it empty if you don't need it",
    )

    args = parser.parse_args()

    main(**vars(args))
