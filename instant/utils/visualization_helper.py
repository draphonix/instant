import matplotlib.pyplot as plt

# Data Provided
endpoints = [
    '/wp_rbe_tools/r44/addit/$1',
    '/wp_rbe_tools/ajax_get_rbe$',
    '/wp_rbe_tools/ajax_get_exist_rbe_n...',
    '/wp_rbe_tools/r44/addit/(?<id>.*)...',
    '/wp_rbe_tools/ajax_save_rbe_event$'
]
median_durations = [1290, 187, 47, 506, 16000]

# Creating the Bar Chart
plt.figure(figsize=(12, 8))  # Increase figure size
bars = plt.bar(endpoints, median_durations, color='skyblue')
plt.xlabel('API Endpoint')
plt.ylabel('Median Duration (ms)')
plt.title('API Endpoints Median Duration')

# Adding median values on top of the bars
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, yval + 50, yval, ha='center', va='bottom')

plt.xticks(rotation=90)  # Rotate x-axis labels for better readability
plt.tight_layout()  # Adjust layout to fit labels
plt.show()
