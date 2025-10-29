try:
    from typing import List, Optional
except ImportError:
    pass

from displayio import Group
from terminalio import FONT
from fruity_menu.abstract import AbstractMenu
from adafruit_display_text.label import Label
from adafruit_datetime import date, datetime, time

PADDING_V_PX = 1
PADDING_H_PX = 4
LEFT_PAD = 1 # Fix graphical issue where text isn't centered in its own drawn box

class AdjustMenu(AbstractMenu):
    label: str = ''
    property = None
    on_value_set = None
    on_value_set_args = None

    def __init__(self, label: str, height: int, width: int, on_value_set = None, on_value_set_args = None):
        self.label = label
        self._width = width
        self._height = height
        self.on_value_set = on_value_set
        self.on_value_set_args = on_value_set_args

    def get_display_io_group(self) -> Group:
        pass

    def get_title_label(self):
        title = Label(FONT, padding_top=PADDING_V_PX, padding_bottom=PADDING_V_PX,padding_right=PADDING_H_PX,padding_left=PADDING_H_PX)
        title.text = self.label
        title.anchor_point = (0.5, 0)
        title.anchored_position = (self._width / 2, 0)
        
        title.color = 0x000000
        title.background_color = 0xffffff
        return title


class BoolMenu(AdjustMenu):
    """Menu for adjusting the value of a Boolean variable"""

    text_when_true = 'True'
    """Text to display when the target variable is True"""

    text_when_false = 'False'
    """Text to display when the target variable is False"""

    def __init__(self, property: bool, label: str, height: int, width: int, value_set = None,
                value_set_args = None, text_true: str = 'True', text_false: str = 'False'):
        """Instantiates a menu to adjust the value of a Boolean variable"""
        self.property = property
        self.text_when_false = text_false
        self.text_when_true = text_true
        super().__init__(label, height, width, value_set, value_set_args)

    def build_displayio_group(self):
        """Builds a `displayio.Group` that represents this menu's current state"""
        grp = Group()
        title_label = self.get_title_label()
        grp.append(title_label)

        prop_text = Label(FONT)
        if (self.property):
            prop_text.text = self.text_when_true
        else:
            prop_text.text = self.text_when_false
        prop_text.anchor_point = (0.5, 0.5)
        prop_text.anchored_position = (self._width / 2, self._height / 2)
        grp.append(prop_text)

        return grp

    def click(self):
        """Invokes the menu's stored action, if any, and returns False."""
        if (self.on_value_set is not None):
            if (self.on_value_set_args is not None):
                self.on_value_set(self.on_value_set_args, self.property)
            else:
                self.on_value_set(self.property)
        return False

    def scroll(self, delta: int):
        """Inverts the stored Boolean variable if the given delta is an odd number"""
        if delta % 2 == 1:
            self.property = not self.property
    
class NumberMenu(AdjustMenu):
    """Menu for adjusting the value of a numeric variable"""

    scroll_factor = 1
    """Multiplies the scroll delta by this number to determine how much to adjust the numeric variable"""
    
    min = None
    """Minimum allowed value"""
    
    max = None
    """Max allowed value"""

    def __init__(self, number, label: str, height: int, width: int, value_set = None,
                value_set_args = None, scroll_mulitply_factor: int = 1, min_value = None, max_value = None):
        """Instantiates a menu to adjust the value of a numeric variable"""
        self.property = number
        self.scroll_factor = scroll_mulitply_factor
        self.min = min_value
        self.max = max_value
        if (self.min is not None and self.max is not None and self.min > self.max):
            raise ValueError('Minimum allowed value is higher than the maximum allowed')
        super().__init__(label, height, width, value_set, value_set_args)

    def build_displayio_group(self):
        """Builds a `displayio.Group` that represents this menu's current state"""
        grp = Group()
        title_label = self.get_title_label()
        grp.append(title_label)

        prop_text = Label(FONT)
        prop_text.text = str(self.property)
        prop_text.anchor_point = (0.5, 0.5)
        prop_text.anchored_position = (self._width / 2, self._height / 2)
        grp.append(prop_text)
        return grp

    def click(self):
        """Invokes the menu's stored action, if any, and returns False"""
        if (self.on_value_set is not None):
            if (self.on_value_set_args is not None):
                self.on_value_set(self.on_value_set_args, self.property)
            else:
                self.on_value_set(self.property)
        return False

    def scroll(self, delta: int):
        """Increments the stored numeric variable by the delta multiplied by the scrolling factor."""
        post_scroll_value = self.property + (self.scroll_factor * delta)
        if (self.min is not None and post_scroll_value < self.min):
            self.property = self.min
        elif (self.max is not None and post_scroll_value > self.max):
            self.property = self.max
        else:
            self.property = post_scroll_value


class OptionMenu(AdjustMenu):
    """Menu for adjusting the value of a numeric variable"""

    options: List
    """List of suitable values"""
    option_labels: Optional[List]
    """Labels for values"""

    def __init__(self, value, options: List, label: str, height: int, width: int,
                 option_labels: Optional[List]=None, value_set=None, value_set_args=None):
        """Instantiates a menu to adjust the value of a numeric variable"""
        self.options = options
        try:
            self.index = self.options.index(value)
        except ValueError:
            raise ValueError("Value must be present in options")
        self.option_labels = option_labels
        if self.option_labels is not None:
            if len(self.option_labels) != len(self.options):
                raise ValueError("options and value_labels must be the same length")
        super().__init__(label, height, width, value_set, value_set_args)

    @property
    def property(self):
        return self.options[self.index]

    def build_displayio_group(self):
        """Builds a `displayio.Group` that represents this menu's current state"""
        grp = Group()
        title_label = self.get_title_label()
        grp.append(title_label)

        prop_text = Label(FONT)
        if self.option_labels is not None:
            prop_text.text = str(self.option_labels[self.index])
        else:
            prop_text.text = str(self.property)
        prop_text.anchor_point = (0.5, 0.5)
        prop_text.anchored_position = (self._width / 2, self._height / 2)
        grp.append(prop_text)
        return grp

    def click(self):
        """Invokes the menu's stored action, if any, and returns False"""
        if self.on_value_set is not None:
            if self.on_value_set_args is not None:
                self.on_value_set(self.on_value_set_args, self.property)
            else:
                self.on_value_set(self.property)
        return False

    def scroll(self, delta: int):
        """Increments to the next or previous value."""
        self.index = (self.index + delta) % len(self.options)
        
        
class DateMenu(AdjustMenu):
    """Menu for adjusting the value of a date variable (Tuple or dictionary of year, month, day, maybe hour, minute and second.)"""

    scroll_factor = 1
    """Multiplies the scroll delta by this number to determine how much to adjust the numeric variable"""
    
    month_days = (30, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
    month_min = 1
    month_max = 12
    lims = {"year": (2025, None), "month": (1, 12), "day": (1, None)}
    """(Minimum, Maximum) allowed value, inclusive
        Maximum for day is determined by the month."""
    
    
    separator = '-'
    
    x_offset = 7 # Pixels to shift text to re-align to center
    

    def __init__(self, dt: adafruit_datetime.date, label: str, height: int, width: int, value_set = None,
                value_set_args = None, scroll_mulitply_factor: int = 1, min_date: date = None, max_date: date = None):
        """Instantiates a menu to adjust the value of a numeric variable"""
        self.date = [dt.year, dt.month, dt.day]
        self.select = 0
        self.min_date = min_date
        self.max_date = max_date
        if (self.min_date is not None and self.max is not None and self.min > self.max):
            raise ValueError('Minimum allowed value is higher than the maximum allowed')
        super().__init__(label, height, width, value_set, value_set_args)

    def build_displayio_group(self):
        """Builds a `displayio.Group` that represents this menu's current state"""
        grp = Group()
        title_label = self.get_title_label()
        grp.append(title_label)
        
        bl = 0x000000
        wh = 0xffffff

        ''' Make multiple labels that display current time '''
        
        # Creating three labels to store relevant properties
        year_text = Label(FONT, text=f'{self.date[0]}', padding_left=1, anchor_point=(1.0, 0.5), 
                            anchored_position=(self._width/2 - 15 + self.x_offset, self._height/2))
        
        month_text = Label(FONT, text=f'{self.date[1]:02}', padding_left=1, anchor_point = (0.5, 0.5),
                            anchored_position = (self._width/2 + self.x_offset, self._height/2))
        day_text = Label(FONT, text=f'{self.date[2]:02}', padding_left=1, anchor_point = (0.0, 0.5),
                            anchored_position = (self._width/2 + 15 + self.x_offset, self._height/2))
        
        ym_sep_text = Label(FONT, text = self.separator, anchor_point = (1.0, 0.5),
                               anchored_position = (self._width/2 - 7 + self.x_offset, self._height/2))
        md_sep_text = Label(FONT, text = self.separator, anchor_point = (0.0, 0.5),
                               anchored_position = (self._width/2 + 7 + self.x_offset, self._height/2))
        if self.select == 2:
                day_text.color = bl
                day_text.background_color = wh
        elif self.select == 1:
                month_text.color = bl
                month_text.background_color = wh
        else:
                year_text.color = bl
                year_text.background_color = wh
        
        grp.append(year_text)
        grp.append(ym_sep_text)
        grp.append(month_text)
        grp.append(md_sep_text)
        grp.append(day_text)
        return grp

    def click(self):
        """Invokes the menu's stored action, if any, and returns False"""
        self.select += 1
        if self.select > 2:
            ''' Return concatenated date object '''
            self.select = 0
            date_obj = date(*self.date)
            if (self.on_value_set is not None):
                if (self.on_value_set_args is not None):
                    self.on_value_set(self.on_value_set_args, date_obj)
                else:
                    self.on_value_set(date_obj)
            return False
        return True

    def scroll(self, delta: int):
        """Increments the stored numeric variable by the delta multiplied by the scrolling factor."""
        self.date[self.select] = self.date[self.select] + delta
        
        # Restrict months to valid values 
        self.date[1] = self.clamp(self.date[1], self.month_min, self.month_max)
        
        max_days = self.days_in_month(self.date[0], self.date[1])
        self.date[2] = self.clamp(self.date[2], 1, max_days)
        
        
    def clamp(self, n, minn, maxn):
        return max(min(maxn, n), minn)
    
    def days_in_month(self, year, month):
        """Leap day edgecases are a lot more complicated than expected"""
        if month == 2 and year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
            return 29
 
        elif month == 2:
            return 28
 
        elif month == 4 or month == 6 or month == 9 or month == 11:
            return 30
        
        elif month <= 12 and month > 0:
            return 31
        
        return None
        
          
class TimeMenu(AdjustMenu):
    """Menu for adjusting the value of a date variable (Tuple or dictionary of year, month, day, maybe hour, minute and second.)"""

    scroll_factor = 1
    """Multiplies the scroll delta by this number to determine how much to adjust the numeric variable"""
    
    month_lengths = (30, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
    
    lims = {"year": (2025, None), "month": (1, 12), "day": (1, None)}
    """(Minimum, Maximum) allowed value, inclusive
        Maximum for day is determined by the month."""

    

    def __init__(self, tm: time, label: str, height: int, width: int, value_set = None,
                value_set_args = None, scroll_mulitply_factor: int = 1, min_date: time = None, max_date: time = None):
        """Instantiates a menu to adjust the value of a numeric variable"""
        
        self.cur_index = 0
        """ Tracks the portion of the date that the menu is currently adjusting."""
        
        self.property = tm

        super().__init__(label, height, width, value_set, value_set_args)

    def build_displayio_group(self):
        """Builds a `displayio.Group` that represents this menu's current state"""
        grp = Group()
        title_label = self.get_title_label()
        grp.append(title_label)

        """ Make multiple labels that display current time """
        year_text = [Label(FONT, text="  ")] * 3 
        year_text[0].text = self.property.year
        hour_text[0].anchor_point = (1.0, 0.5)
        
        _text[1].text = self.property.month
        prop_text.anchor_point = (1.0, 0.5)
        
        date_text[2].text = self.property.day
        prop_text.anchor_point = (1.0, 0.5)
        
        prop_text.anchored_position = (self._width / 2, self._height / 2)
        grp.append(prop_text)
        return grp

    def click(self):
        """Invokes the menu's stored action, if any, and returns False"""
        
        if (self.on_value_set is not None):
            if (self.on_value_set_args is not None):
                self.on_value_set(self.on_value_set_args, self.property)
            else:
                self.on_value_set(self.property)
        return False

    def scroll(self, delta: int):
        """Increments the stored numeric variable by the delta multiplied by the scrolling factor."""
        post_scroll_value = self.property + (self.scroll_factor * delta)
        if (self.min is not None and post_scroll_value < self.min):
            self.property = self.min
        elif (self.max is not None and post_scroll_value > self.max):
            self.property = self.max
        else:
            self.property = post_scroll_value
