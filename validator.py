def validate_text(text, poster_type):
    try:
        paragraphs = text.split('\n\n')  
        words = text.split()

        if poster_type == "basic":
            max_words = 20
            if len(words) > max_words:
                return False
            else:
                return True

        elif poster_type == "postcard":
            max_words_per_paragraph = 50
            if len(paragraphs) > 1:
                return False
            elif len(words) > max_words_per_paragraph:
                return False
            else:
                return True

        elif poster_type == "invitation":
            max_paragraphs = 2
            if len(paragraphs) > max_paragraphs:
                return False
            else:
                return True

        else:
            return False

    except Exception:
        return True


def validate_title(title, poster_type):
    try:
        words = title.split()

        if poster_type == "basic":
            min_words = 1
            max_words = 10
            if len(words) < min_words or len(words) > max_words:
                return False
            else:
                return True, None

        elif poster_type in ["postcard", "invitation"]:
            required_words = 2
            if len(words) != required_words:
                return False
            else:
                return True, None

        else:
            return False
    except Exception:
        return True
