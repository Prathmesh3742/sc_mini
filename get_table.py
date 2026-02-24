import main
df = main.df_comparison
with open('table_out.md', 'w') as f:
    f.write(df.to_markdown(index=False))
