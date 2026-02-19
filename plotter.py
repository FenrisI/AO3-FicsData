import matplotlib.pyplot as plt
import itertools
import os

PLOT_BASE_COLOR = "#12ACAE"
STYLE_CONFIG = {
    'figure.figsize': (10, 6),
    'figure.dpi': 150,
    'axes.titlesize': 14,
    'axes.labelsize': 12,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'grid.color': '#e0e0e0',
    'grid.linestyle': '--',
    'grid.alpha': 0.6,
}

plt.style.use('bmh')
plt.rcParams.update(STYLE_CONFIG)

# plt.plot([x for x in range(1, len(counts)+1)], counts.values(),
#          color=, marker='o', linestyle='-')

def plot_chapter_word_counts(chapter_data: dict[int, int], save_to: str = None):
    """
    Bar chart showing per chapter word count.
    """
    chapters = list(chapter_data.keys())
    word_counts = list(chapter_data.values())

    plt.figure(figsize=(10, 6))

    plt.bar(chapters, word_counts, color=PLOT_BASE_COLOR,
            edgecolor="black")
    
    plt.title("Word Counts per Chapter")
    plt.xlabel("Chapter")
    plt.ylabel("Words")
    
    plt.tight_layout()

    if save_to:
        save_plot(save_to)

    plt.show()

def plot_cumulative_word_counts(chapter_data: dict[int, int], save_to: str = None):
    """
    Line chart showing total word count growth over chapters.
    """
    chapters = list(chapter_data.keys())
    cumulative_counts = list(itertools.accumulate(chapter_data.values()))

    plt.figure()
    plt.plot(chapters, cumulative_counts, marker='o', linestyle='-', color=PLOT_BASE_COLOR, linewidth=2)
    plt.fill_between(chapters, cumulative_counts, color='lightblue', alpha=0.3) # shading effect
    
    plt.title("Total Word Count Progression")
    plt.xlabel("Chapter")
    plt.ylabel("Total Words")
    plt.xticks(chapters)
    plt.grid(True)
    
    plt.tight_layout()

    if save_to:
        save_plot(save_to)

    plt.show()

def plot_top_words(frequency_map: dict[str, int], top_n: int = 10, save_to: str = None):
    """
    Horizontal bar chart of the top N most frequent words.
    """
    # sorting the dictionary in descending order by value
    top_items = frequency_map.most_common(top_n)
    
    # Unzip into two lists (and reverse them so the highest bar is at the top)
    words, counts = zip(*top_items[::-1])
    
    plt.figure()
    plt.barh(words, counts, color='salmon', edgecolor='black')
    
    plt.title(f"Top {top_n} Most Frequent Words")
    plt.xlabel("Frequency")
    plt.grid(axis='y')
    
    plt.tight_layout()

    if save_to:
        save_plot(save_to)

    plt.show()

def save_plot(filename: str, output_dir: str = "plots"):
    """
    Saves the current active plot to a file.
    Ensures the output directory exists.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    full_path = os.path.join(output_dir, filename)

    try:
        plt.savefig(full_path, bbox_inches='tight')
    except Exception as e:
        print(f"Error saving plot: {e}")