from db_connection import return_engine_and_session, Comment, Article

engine, session = return_engine_and_session()


def get_comments(amount=20, best_or_worst="best", article_id=0):
    # Returning the best or worst comments with their info
    # Joining together both comment and article tables
    if article_id not in ["0", "", 0]:
        if best_or_worst == "best":
            result = session.query(Comment, Article).\
                filter(Comment.article_id == article_id).\
                filter(Comment.article_id == Article.id).\
                order_by(Comment.plus.desc())[:amount]
        else:
            result = session.query(Comment, Article).\
                filter(Comment.article_id == article_id).\
                filter(Comment.article_id == Article.id).\
                order_by(Comment.minus.desc())[:amount]
    else:
        if best_or_worst == "best":
            result = session.query(Comment, Article).\
                filter(Comment.article_id == Article.id).\
                order_by(Comment.plus.desc())[:amount]
        else:
            result = session.query(Comment, Article).\
                filter(Comment.article_id == Article.id).\
                order_by(Comment.minus.desc())[:amount]

    # Transforming the results into a dictionary, so it can be sent
    #   through JSON
    result_in_dict = []
    for comment, article in result:
        dict_entry = {
            "content": comment.content,
            "plus": comment.plus,
            "minus": comment.minus,
            "link": article.link,
            "article_name": article.name,
            "comment_amount": article.comment_amount,
        }
        result_in_dict.append(dict_entry)

    # print(result_in_dict)
    return result_in_dict


def get_articles():
    # Getting all the articles from newest to oldest
    result = session.query(Article).order_by(Article.id.desc())

    # Transforming the results into a dictionary, so it can be sent
    #   through JSON
    result_in_dict = []
    for article in result:
        dict_entry = {
            "id": article.id,
            "name": article.name,
            "link": article.link,
            "comment_amount": article.comment_amount,
        }
        result_in_dict.append(dict_entry)

    # print(result_in_dict)
    return result_in_dict


if __name__ == "__main__":
    get_comments(10)
    # get_articles()
