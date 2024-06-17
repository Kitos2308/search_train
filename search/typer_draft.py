import typer

app = typer.Typer()


@app.command()
def start(app_name:str):
    print(f'start {app_name}')


@app.command()
def hello(name: str):
    print(f"Hello {name}")

if __name__=='__main__':
    app()