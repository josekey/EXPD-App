import pandas as pd

df = pd.DataFrame({
    'brand': ['Yum Yum', 'Yum Yum', 'Indomie', 'Indomie', 'Indomie'],
    'style': ['cup', 'cup', 'cup', 'pack', 'pack'],
    'rating': [4, 4, 3.5, 15, 5]
})

print(f'original:\n{df}')

# df.drop_duplicates()
df.drop_duplicates(subset=None, keep="first", inplace=True)

print(f'no duplicates:\n{df}')

df = df.sort_values(by = ['brand','style'])

print(f'sorted:\n{df}')