import texts


class User:
    def __init__(
        self,
        id,
        name=None,
        phone_number=None,
        is_admin=False,
        font="Ray",
        color1="#2C347C",
        color2="#F8BA19",
        color_text="#FFFFFF",
    ):
        self.id = id
        self.name = name
        self.phone_number = phone_number
        self.is_admin = is_admin
        self.font = font
        self.color1 = color1
        self.color2 = color2
        self.color_text = color_text

    def __str__(self):
        return texts.user_profile.format(
            name=self.name,
            phone_number=self.phone_number,
        )

    def needs_registration(self):
        return self.name is None


class Poster:
    def __init__(
        self,
        id,
        date=None,
        user_id=None,
        font="Ray",
        color1="#2C347C",
        color2="#F8BA19",
        text_color="#FFFFFF",
        template=None,
        orientation=None,
        initial_image=None,
        title=None,
        message_text=None,
        output_image=None,
    ):
        self.id = id
        self.date = date
        self.user_id = user_id
        self.font = font
        self.color1 = color1
        self.color2 = color2
        self.text_color = text_color
        self.template = template
        self.orientation = orientation
        self.initial_image = initial_image
        self.title = title
        self.message_text = message_text
        self.output_image = output_image

    def __str__(self):
        return texts.poster_details.format(
            title=self.title,
            message_text=self.message_text,
            orientation=self.orientation,
            output_image=self.output_image,
        )

    def is_complete(self):
        """Check if the poster has all required attributes."""
        return all(
            [
                self.title is not None,
                self.message_text is not None,
                self.initial_image is not None,
                self.output_image is not None,
            ]
        )
