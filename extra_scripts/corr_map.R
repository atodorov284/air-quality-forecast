library(ggplot2)
library(reshape2)
library(dplyr)
library(extrafont)

loadfonts(device = "pdf")  # Load fonts

correlation_matrix <- read.csv(file.choose(), row.names = 1)

correlation_matrix[abs(correlation_matrix) < 0.3] <- NA

correlation_matrix[lower.tri(correlation_matrix)] <- NA
diag(correlation_matrix) <- NA

melted_cor <- melt(as.matrix(correlation_matrix), na.rm = TRUE)

melted_cor$fill_value <- ifelse(is.na(melted_cor$value), NA, melted_cor$value)

ggplot(melted_cor, aes(x = Var1, y = Var2)) +
  geom_tile(aes(fill = fill_value), color = "black") +
  labs(x = NULL, y = NULL, fill = "Pearson's\nCorrelation") +
  scale_fill_gradient2(mid = "#FBFEF9", low = "#0C6291", high = "#A63446", 
                       limits = c(-1, 1), na.value = "lightgray") +
  theme_classic() +
  scale_x_discrete(expand = c(0, 0)) +
  scale_y_discrete(expand = c(0, 0)) +
  theme(text = element_text(family = "Arial"),  # Use a common font
        plot.title = element_text(size = 14, family = "Arial"),  # Title font
        axis.text.x = element_text(angle = 45, hjust = 1),
        legend.position = "right",  # Position of the legend
        legend.title = element_text(size = 12),  # Title size
        legend.text = element_text(size = 10),  # Text size
        legend.key.size = unit(1.5, "cm"),  # Size of the legend keys
        legend.key.width = unit(1, "cm"))  # Width of the legend keys
