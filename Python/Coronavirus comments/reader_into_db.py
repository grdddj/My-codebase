import glob
import json
import os

from db_connection import Article, Comment, return_engine_and_session

engine, session = return_engine_and_session()


def get_all_files_with_given_extension(folder, extension):
    """
    Returning all files with a given extension from the same directory as the script
    """

    path_of_the_file = os.path.dirname(os.path.realpath(__file__))
    all_files = glob.glob(
        os.path.join(path_of_the_file, folder, "*.{}".format(extension))
    )
    return all_files


def process_file(file_name):
    with open(file_name, "r") as results_file:
        content = json.load(results_file)
        article_id = int(content.get("article_id"))
        article_name = content["article_name"]
        article_link = content["article_link"]
        comment_amount = content.get("amount")
        print("article_id", article_id)
        print("article_name", article_name)
        print("comment_amount", comment_amount)

        already_there = (
            session.query(Comment).filter(Comment.article_id == article_id).count()
        )
        print("already_there", already_there)

        # Making sure we are not "updating" with probably older comments
        if already_there > comment_amount:
            print("NOT UPDATING THIS ONE")
            return

        # Deleting all the previous comments, so that we have no duplicates
        session.query(Comment).filter(Comment.article_id == article_id).delete()

        # Upserting the article, in case it already exists
        article = Article(
            id=article_id,
            name=article_name,
            link=article_link,
            comment_amount=comment_amount,
        )
        upserted_article = session.merge(article)
        session.add(upserted_article)

        # Including all the new articles
        for comment in content.get("comments", []):
            author = comment.get("name")
            plus = comment.get("plus")
            minus = comment.get("minus")
            content = comment.get("content")
            comment = Comment(
                article_id=article_id,
                author=author,
                content=content,
                plus=plus,
                minus=minus,
            )
            session.add(comment)

    # Saving all the changes
    session.commit()


def save_all_files_from_a_folder_into_db(folder_name):
    extension = "json"
    all_files = get_all_files_with_given_extension(folder_name, extension)
    for file in all_files:
        print(file)
        process_file(file)

    print(len(all_files))


if __name__ == "__main__":
    folder_name = "Fifth_try"
    save_all_files_from_a_folder_into_db(folder_name)
