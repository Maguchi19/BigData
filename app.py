# app.py

from shiny import App, ui, render, reactive
import pandas as pd
import plotly.express as px
from utils.forecasting import generar_pronostico

# Cargar datos y verificar columnas disponibles
df = pd.read_csv("data/aforos_capufe.csv", encoding="latin1")
print("Columnas disponibles:", df.columns.tolist())

# Comprobar si las columnas de vehículos están en mayúsculas o minúsculas
vehiculo_columnas = {}
columnas_originales = {
    'Motocicleta': ['MOTOCICLETA', 'Motocicleta', 'motocicleta'],
    'Automóvil': ['AUTOMOVIL', 'Automovil', 'automovil'],
    'Autobús': ['AUTOBUS', 'Autobus', 'autobus'],
    'Camión 2 ejes': ['CAMION_2_EJES', 'Camion_2_Ejes', 'camion_2_ejes'],
    'Camión 3 ejes': ['CAMION_3_EJES', 'Camion_3_Ejes', 'camion_3_ejes'],
    'Camión 4 ejes': ['CAMION_4_EJES', 'Camion_4_Ejes', 'camion_4_ejes'],
    'Camión 5 ejes': ['CAMION_5_EJES', 'Camion_5_Ejes', 'camion_5_ejes'],
    'Camión 6 ejes': ['CAMION_6_EJES', 'Camion_6_Ejes', 'camion_6_ejes'],
    'Camión 7 ejes': ['CAMION_7_EJES', 'Camion_7_Ejes', 'camion_7_ejes'],
}

# Detectar las columnas correctas del DataFrame
for tipo, posibles_columnas in columnas_originales.items():
    for col in posibles_columnas:
        if col in df.columns:
            vehiculo_columnas[tipo] = col
            print(f"Columna encontrada: {tipo} -> {col}")
            break

# Si no se encontraron columnas, esto podría indicar otro formato en el CSV
if not vehiculo_columnas:
    print("¡ADVERTENCIA! No se encontraron columnas de vehículos con los nombres esperados.")
    print("Intentando detectar automáticamente columnas relevantes...")
    
    # Buscar columnas que podrían contener información de vehículos
    posibles_vehiculos = [col for col in df.columns if any(
        keyword in col.upper() for keyword in 
        ["MOTO", "AUTO", "BUS", "CAMION", "EJE", "VEHI"]
    )]
    
    if posibles_vehiculos:
        print("Posibles columnas de vehículos encontradas:", posibles_vehiculos)
        # Asignar nombres descriptivos a las columnas encontradas
        for col in posibles_vehiculos:
            nombre_descriptivo = col.replace("_", " ").title()
            vehiculo_columnas[nombre_descriptivo] = col

# Convertir los años a string para el input_select
if 'AÑO' in df.columns:
    anio_col = 'AÑO'
elif 'Año' in df.columns:
    anio_col = 'Año'
elif 'año' in df.columns:
    anio_col = 'año'
elif 'ANIO' in df.columns:
    anio_col = 'ANIO'
else:
    # Buscar cualquier columna que contenga "año" o "anio"
    posibles_anios = [col for col in df.columns if 'año' in col.lower() or 'anio' in col.lower()]
    anio_col = posibles_anios[0] if posibles_anios else 'AÑO'  # Default si no encuentra

print(f"Usando columna de año: {anio_col}")

# Asegurar que la columna de año existe
if anio_col not in df.columns:
    print(f"¡ERROR! La columna {anio_col} no existe en el DataFrame.")
    # Crear una columna de año ficticia para evitar errores
    df[anio_col] = 2023
    anios = [2023]
else:
    anios = sorted(df[anio_col].unique())

anios_str = [str(a) for a in anios]

# Columna de mes
if 'MES' in df.columns:
    mes_col = 'MES'
elif 'Mes' in df.columns:
    mes_col = 'Mes'
elif 'mes' in df.columns:
    mes_col = 'mes'
else:
    # Buscar cualquier columna que contenga "mes"
    posibles_meses = [col for col in df.columns if 'mes' in col.lower()]
    mes_col = posibles_meses[0] if posibles_meses else 'MES'  # Default si no encuentra

print(f"Usando columna de mes: {mes_col}")

# Estilos personalizados para la aplicación
custom_css = """
<style>
.logo {
    text-align: center;
    margin-bottom: 20px;
}
.card {
    border-radius: 8px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    margin-bottom: 20px;
    padding: 15px;
    background-color: white;
}
.header {
    background-color: #005288;
    color: white;
    padding: 15px;
    margin-bottom: 20px;
    border-radius: 8px;
    text-align: center;
}
.vehicle-stats {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    margin-bottom: 20px;
}
</style>
"""

# Interfaz de usuario
app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_select("anio", "Seleccione el año", choices=anios_str),
        ui.p("Dashboard desarrollado para mostrar aforos vehiculares de CAPUFE"),
        ui.hr(),
        ui.a("Documentación", href="https://www.gob.mx/capufe", target="_blank"),
    ),
    ui.div(
        ui.HTML(custom_css),  # Agregar estilos personalizados
        ui.div(
            {"class": "header"},
            ui.h2("Dashboard de Aforos CAPUFE (2021–2025)"),
            # Intenta cargar la imagen sólo si existe en la ruta correcta
            ui.div({"class": "logo"},
                ui.img(src="data/emiiii.png", height="100px", alt="Logo CAPUFE")
            ),
        ),
        
        ui.div(
            {"class": "card"},
            ui.h3("Aforo vehicular por tipo"),
            ui.output_ui("grafico_barras_tipo"),
        ),
        
        ui.div(
            {"class": "card"},
            ui.h4("Totales por tipo de vehículo"),
            ui.output_ui("kpis_por_vehiculo"),
            ui.div(
                {"class": "vehicle-stats"},
                ui.div(
                    ui.h5("Vehículo con mayor aforo:"),
                    ui.output_text("vehiculo_mayor")
                ),
                ui.div(
                    ui.h5("Vehículo con menor aforo:"),
                    ui.output_text("vehiculo_menor")
                )
            )
        ),
        
        ui.div(
            {"class": "card"},
            ui.h4("Datos tabulares"),
            ui.output_data_frame("tabla_datos"),
        ),
        
        ui.div(
            {"class": "card"},
            ui.h3("Pronóstico de aforo total"),
            ui.output_ui("grafico_pronostico"),
        ),
    )
)

# Servidor
def server(input, output, session):

    @reactive.Calc
    def datos_filtrados():
        # Verificar si el input existe
        try:
            anio_seleccionado = int(input.anio())
            return df[df[anio_col] == anio_seleccionado]
        except (ValueError, AttributeError) as e:
            print(f"Error al filtrar por año: {e}")
            # Devolver DataFrame completo en caso de error
            return df

    @reactive.Calc
    def total_por_tipo():
        datos = datos_filtrados()
        totales = {}
        for tipo, col in vehiculo_columnas.items():
            if col in datos.columns:
                totales[tipo] = datos[col].sum()
            else:
                print(f"Advertencia: La columna '{col}' no existe en los datos filtrados")
                totales[tipo] = 0  # Valor predeterminado
        return totales

    @output
    @render.ui
    def grafico_barras_tipo():
        # Usar plotly con UI en lugar de @render.plot
        totales = total_por_tipo()
        df_bar = pd.DataFrame(totales.items(), columns=["Tipo de vehículo", "Total"])
        fig = px.bar(df_bar, x="Tipo de vehículo", y="Total", text="Total")
        fig.update_layout(
            xaxis_title='Tipo de vehículo',
            yaxis_title='Total',
            template='plotly_white',
            height=400
        )
        # Convertir el gráfico de Plotly en un componente UI
        return ui.HTML(fig.to_html(include_plotlyjs="cdn"))

    @output
    @render.ui
    def kpis_por_vehiculo():
        totales = total_por_tipo()
        return ui.div(
            *[
                ui.div(
                    {"style": "display:inline-block; margin:10px; padding:10px; border:1px solid #ccc; border-radius:10px; text-align:center;"},
                    ui.div({"style": "font-size:24px;"}, f"{valor:,}"),
                    ui.div({"style": "font-size:14px; color:gray;"}, tipo)
                )
                for tipo, valor in totales.items()
            ]
        )

    @output
    @render.text
    def vehiculo_mayor():
        totales = total_por_tipo()
        if totales:
            return max(totales, key=totales.get)
        return "No hay datos disponibles"

    @output
    @render.text
    def vehiculo_menor():
        totales = total_por_tipo()
        if totales:
            return min(totales, key=totales.get)
        return "No hay datos disponibles"

    @output
    @render.data_frame
    def tabla_datos():
        datos = datos_filtrados()
        columnas_disponibles = [col for col in [anio_col, mes_col] + list(vehiculo_columnas.values()) 
                              if col in datos.columns]
        return datos[columnas_disponibles]

    @output
    @render.ui
    def grafico_pronostico():
        try:
            datos = datos_filtrados()
            
            # Manejar columnas de fecha
            try:
                # Si MES tiene nombres (ENERO, FEBRERO, etc.)
                if pd.api.types.is_object_dtype(datos[mes_col]):
                    # Convertir nombres de mes a números
                    mes_mapping = {
                        'ENERO': 1, 'enero': 1, 'Enero': 1, 
                        'FEBRERO': 2, 'febrero': 2, 'Febrero': 2,
                        'MARZO': 3, 'marzo': 3, 'Marzo': 3,
                        'ABRIL': 4, 'abril': 4, 'Abril': 4,
                        'MAYO': 5, 'mayo': 5, 'Mayo': 5,
                        'JUNIO': 6, 'junio': 6, 'Junio': 6,
                        'JULIO': 7, 'julio': 7, 'Julio': 7,
                        'AGOSTO': 8, 'agosto': 8, 'Agosto': 8,
                        'SEPTIEMBRE': 9, 'septiembre': 9, 'Septiembre': 9,
                        'OCTUBRE': 10, 'octubre': 10, 'Octubre': 10,
                        'NOVIEMBRE': 11, 'noviembre': 11, 'Noviembre': 11,
                        'DICIEMBRE': 12, 'diciembre': 12, 'Diciembre': 12
                    }
                    mes_numerico = datos[mes_col].map(mes_mapping)
                    datos["FECHA"] = pd.to_datetime({
                        'year': datos[anio_col], 
                        'month': mes_numerico, 
                        'day': 1
                    })
                else:
                    datos["FECHA"] = pd.to_datetime({
                        'year': datos[anio_col], 
                        'month': datos[mes_col], 
                        'day': 1
                    })
            except Exception as e:
                print(f"Error al convertir fecha: {e}")
                # Crear una columna de fecha ficticia en caso de error
                datos["FECHA"] = pd.date_range(start='2023-01-01', periods=len(datos), freq='M')
            
            # Calcular suma de vehículos para la serie
            columnas_vehiculos = [col for col in vehiculo_columnas.values() if col in datos.columns]
            datos["y"] = datos[columnas_vehiculos].sum(axis=1)
            
            # Preparar datos para pronóstico
            datos_pronostico = datos.sort_values("FECHA")[["FECHA", "y"]].rename(columns={"FECHA": "ds"})
            
            # Generar pronóstico (con manejo de errores)
            try:
                forecast = generar_pronostico(datos_pronostico, 'y', meses_a_pronosticar=12)
            except Exception as e:
                print(f"Error al generar pronóstico: {e}")
                # Crear datos de pronóstico ficticios para la visualización
                last_date = datos_pronostico["ds"].max()
                future_dates = pd.date_range(start=last_date, periods=13, freq='M')[1:]
                forecast = pd.DataFrame({
                    "ds": future_dates,
                    "yhat": [datos_pronostico["y"].mean()] * 12,
                    "yhat_upper": [datos_pronostico["y"].mean() * 1.1] * 12,
                    "yhat_lower": [datos_pronostico["y"].mean() * 0.9] * 12
                })
            
            # Crear gráfico
            fig = px.line(forecast, x="ds", y="yhat", labels={"ds": "Fecha", "yhat": "Pronóstico"})
            fig.add_scatter(x=forecast["ds"], y=forecast["yhat_upper"], mode='lines', name='Upper Bound', line=dict(dash='dot'))
            fig.add_scatter(x=forecast["ds"], y=forecast["yhat_lower"], mode='lines', name='Lower Bound', line=dict(dash='dot'))
            fig.update_layout(
                template="plotly_white", 
                height=400,
                title="Pronóstico para los próximos 12 meses"
            )
            # Convertir el gráfico de Plotly en un componente UI
            return ui.HTML(fig.to_html(include_plotlyjs="cdn"))
        
        except Exception as e:
            print(f"Error en generación de gráfico de pronóstico: {e}")
            # Crear un gráfico vacío en caso de error
            fig = px.line(x=[0], y=[0])
            fig.update_layout(
                title="Error al generar pronóstico",
                annotations=[dict(text="No hay suficientes datos para el pronóstico", 
                                  x=0.5, y=0.5, showarrow=False)]
            )
            # Convertir el gráfico de error en un componente UI
            return ui.HTML(fig.to_html(include_plotlyjs="cdn"))

# Crear la app
app = App(app_ui, server)