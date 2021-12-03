# -*- coding:utf-8 -*-
# --------------------------------------------------------
# Copyright (C), 2016-2021, lizhe, All rights reserved
# --------------------------------------------------------
# @Name:        constant.py
# @Author:      lizhe
# @Created:     2021/11/20 - 12:12
# --------------------------------------------------------

DEFAULT_TIME_OUT = 3

LOCATORS = "resourceId", "className", "xpath", "text", "description"

UISELECTORS = "text", "textContains", "textMatches", "textStartsWith", \
              "className", "classNameMatches", \
              "description", "descriptionContains", "descriptionMatches", "descriptionStartsWith", \
              "checkable", "checked", "clickable", "longClickable", \
              "scrollable", "enabled", "focusable", "focused", "selected", \
              "packageName", "packageNameMatches", \
              "resourceId", "resourceIdMatches", \
              "index", "instance"

LOWER_LOCATORS = list(map(lambda x: x.lower(), LOCATORS))

LOWER_UISELECTORS = list(map(lambda x: x.lower(), UISELECTORS))
