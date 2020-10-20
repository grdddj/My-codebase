import requests
from bs4 import BeautifulSoup
from db_connection_idnes import return_engine_and_session, Comment, Article

engine, session = return_engine_and_session()


link = "https://www.idnes.cz/zpravy/domaci/babis-koronavirus-projev-ct-nova-prima.A200323_133201_domaci_kop/diskuse/8?razeni=time"
link = "https://www.idnes.cz/zpravy/domaci/koronavirus-skolstvi-maturity-prijimaci-zkousky-msmt-plaga.A200323_150620_domaci_brzy/diskuse"


def _is_a_valid_article_link(article_link):
    """
    Determines whether the link is a valid article one
    """
    # It must have a specified string inside it
    specified_string = "A200"
    return specified_string in article_link


def return_all_articles_from_page(link_with_articles):
    # link_with_articles = "https://www.idnes.cz/koronavirus/clanky/7"
    response = requests.get(link_with_articles)
    soup = BeautifulSoup(response.text, "html.parser")

    print("link_with_articles", link_with_articles)
    try:
        results = soup.find(id="list-art-count").findAll(class_="art")
    except:
        print("UNABLE TO LOCATE LIST OF ARTICLES")
        return []
    print("article amount:", len(results))

    articles_and_names = []
    for result in results:
        link_to_article = result.find("a")["href"]
        article_name = result.find("h3").get_text().strip()
        articles_and_names.append((link_to_article, article_name))

    return [a_and_n for a_and_n in articles_and_names if
            _is_a_valid_article_link(a_and_n[0])]


def return_discussion_link(article_link):
    return "{}/diskuse".format(article_link)


def process_name(malformed_name):
    """
    Gets rid of strange numbers in the name, just preserves the letters
    """
    result = []
    for bit in malformed_name:
        try:
            int(bit)
        except ValueError:
            result.append(bit)

    return "".join(result).strip()


def analyze_one_page_with_comments(discussion_link, article_id):
    response = requests.get(discussion_link)
    soup = BeautifulSoup(response.text, "html.parser")
    print("discussion_link", discussion_link)
    try:
        results = soup.find(id="disc-list").findAll(class_="contribution")
    except:
        print("NOT POSSIBLE TO FIND DISCUSSIONS")
        return
    print(len(results))

    for result in results:
        content = result.find(class_="user-text").get_text().strip()
        score = result.find(class_="score").get_text().strip()
        date = result.find(class_="date").get_text().strip()
        print(date)
        name = result.find(class_="name").get_text().strip()
        plus = int(score.split("/")[0].strip("+"))
        minus = 0 if score.split("/")[1] == "0" else int("".join(score.split("/")[1][1:]))
        comment = Comment(article_id=article_id, author=process_name(name),
                          content=content, plus=plus, minus=minus)
        session.add(comment)

    session.commit()


def aggregate_the_pull():
    # for index in range(1, 10):
    for index in range(1, 45):
        link = "https://www.idnes.cz/koronavirus/clanky/{}".format(index)
        all_articles_and_names = return_all_articles_from_page(link)
        for article_link, article_name in all_articles_and_names:
            # Upserting the article, in case it already exists
            article_entry = Article(id=article_name, name=article_name,
                                    link=article_link, comment_amount=50)
            upserted_article = session.merge(article_entry)
            session.add(upserted_article)
            session.commit()

            # Deleting all the previous comments, so that we have no duplicates
            session.query(Comment) \
                .filter(Comment.article_id == article_name).delete()

            discussion_link = return_discussion_link(article_link)

            analyze_one_page_with_comments(discussion_link, article_name)


if __name__ == "__main__":
    # analyze_one_page_with_comments(link)
    # return_all_articles_from_page("d")
    aggregate_the_pull()
