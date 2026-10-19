from mcp.server.fastmcp import FastMCP # type: ignore


mcp = FastMCP("Bmi-server")

print(f"Starting Server {mcp.name}")

@mcp.tool()
def calculate_bmi(weight_kg:float, height_m:float) -> float:
    """
        Calculate the BMI for the givent weight in kg and height in meters
    """

    if height_m <=0:
        raise ValueError("Height must me greater than Zero")
    return weight_kg/(height_m ** 2)

if __name__ == "__main__":
    mcp.run(transport="stdio")

 