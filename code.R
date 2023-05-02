res <- readxl::read_xlsx("~/Downloads/result_5.xlsx")

library(ggplot2)
library(dplyr)

# pre
res <- res %>%
  mutate(
    `Detected Source Language` = as.factor(`Detected Source Language`),
    `Detected Source Language Name` = as.factor(`Detected Source Language Name`),
    Sentiment = as.factor(Sentiment)
  )

# fig 1
res %>%
  group_by(`Detected Source Language`, Sentiment) %>%
  summarise(Count = n()) %>%
  filter(!`Detected Source Language` %in% c("id", "tl", "vi", "zh-TW")) %>%
  rename(Language = `Detected Source Language`) %>%
  ggplot(aes(x = Language, fill = Sentiment, y = Count)) +
  geom_bar(position = "stack", stat = "identity", colour = "black") +
  scale_fill_manual(
    values = c(
      rgb(242, 222, 89, maxColorValue = 255), # MIXED
      rgb(238, 199, 239, maxColorValue = 255), # NEGATIVE
      rgb(247, 247, 247, maxColorValue = 255), # NEUTRAL
      rgb(141, 228, 232, maxColorValue = 255)
    ) # POSITIVE
  ) +
  ggtitle("Newjeans / Youtube reply sentiment") +
  theme(
    plot.title = element_text(size = 30, face = "bold"),
    axis.text = element_text(size = 25),
    axis.title = element_text(size = 25)
  )

set.seed(1234)

# fig 2

res %>%
  group_by(`Translated Text`, Sentiment) %>%
  summarise(
    Value = max(c(Positive, Negative, Neutral, Mixed)) + round(rnorm(1, mean = 1, sd = 1), 3)
  ) %>%
  mutate(fontSize = ifelse(Sentiment == "NEGATIVE", 8, 6)) %>%
  ggplot(aes(x = Sentiment, y = Value, label = `Translated Text`)) +
  geom_text(aes(colour = factor(Sentiment), size = fontSize)) +
  scale_size(range = c(3, 7)) +
  scale_colour_manual(
    values = c(
      "#4F200D", # MIXED
      "#F45050", # NEGATIVE
      "#87CBB9", # NEUTRAL
      "#19376D"
    ) # POSITIVE
  ) +
  ggtitle("Newjeans / Youtube reply sentiment") +
  theme(
    plot.title = element_text(size = 25, face = "bold"),
    axis.text = element_text(size = 20),
    axis.title = element_text(size = 20)
  ) +
  theme(legend.position = "none")

#
# rgb(242,222,89) # yellow : mixed
# rgb(141,228,232) # blue : positive
# rgb(238,199,239) # red : negative
# rgb(247,247,247) # grey : neutral