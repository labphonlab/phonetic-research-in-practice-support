# Exercise 1.1: Reverse-engineer an evidential chain
# Phonetic Research in Practice, companion exercise script (MIT License).
# Run from the repository root; the excerpts printed in the book are taken from this file.

library(tidyverse)
nodes <- read_tsv("nodes.tsv", show_col_types = FALSE) |>
  group_by(layer) |> mutate(y = row_number() - mean(row_number())) |> ungroup()
edges <- read_tsv("edges.tsv", show_col_types = FALSE) |>
  left_join(nodes, by = c(from = "node")) |>
  left_join(nodes, by = c(to = "node"), suffix = c("", "_to"))
p <- ggplot() +
  geom_segment(data = edges, aes(layer, y, xend = layer_to, yend = y_to),
               arrow = arrow(length = unit(2, "mm"))) +
  geom_label(data = nodes, aes(layer, y, label = node, fill = status)) +
  scale_fill_manual(values = c(documented = "white", partial = "grey80", missing = "grey55")) +
  theme_void()
ggsave("evidential_chain.png", p, width = 7, height = 3.5)
