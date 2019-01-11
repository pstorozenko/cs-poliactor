library(tidyverse)
library(patchwork)
data <- read_csv('stability_pd_df.csv', col_types = 'fnn')
data <- data %>% filter(x != 0)

data %>% ggplot(aes(x, y, colour=Person)) +
    geom_point() +
    geom_smooth() +
    xlab('Distance between person\'s embeddings') +
    ylab('Distance between predicted actor\'s embeddings') +
    theme_minimal()

p1 <- data %>% ggplot(aes(x, fill=Person)) +
    geom_histogram()

p2 <- data %>% ggplot(aes(y, fill=Person)) +
    geom_histogram()
p1 + p2

data %>%
    filter(Person=='pasza_s') %>% 
    ggplot(aes(x, y, colour=Person)) +
    geom_point() +
    geom_smooth() +
    xlab('Distance between person\'s embeddings') +
    ylab('Distance between predicted actor\'s embeddings') +
    theme_minimal()

data2 <- read_csv('stability2_pd_df.csv', col_types = 'fnn')
data2 <- data2 %>% filter(x != 0) %>% mutate(diff = y - x)
data2 %>% ggplot(aes(x = Person, y = diff)) +
    geom_boxplot() +
    theme_minimal()

data2 %>% group_by(Person) %>% summarise(mean(diff > 0))

data2 %>% ggplot(aes(x = x, y = y , colour = Person)) +
    geom_point() +
    theme_minimal()
