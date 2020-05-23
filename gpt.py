import streamlit as st
import pandas as pd
import altair as alt


def create_histogram(column, df, df_min, df_max, df_step):
    chart = alt.Chart(df, width=700).mark_bar().encode(
        alt.X(column, bin=alt.Bin(extent=[df_min, df_max], step=df_step)),
        y='count()',
        tooltip=[column, 'count()']
    ).interactive()
    return chart


def main():
    st.image('gpt oee.png', width=700)
    st.sidebar.title('Instruções')
    st.sidebar.markdown('Anexar arquivo csv com os dados a serem analisados')
    st.sidebar.markdown('Escolher colunas com dados que contenham a informação necessária no decorrer do notebook')
    st.sidebar.title('Análise de Tempos')
    st.sidebar.markdown('Notebook desenvolvido para auxiliar a análise de tempos na gestão dos postos de trabalho')
    st.sidebar.title('Cálculo de Eficiência')
    st.sidebar.markdown('Análise realizada com base nos taxas de disponibilidade x performance x qualidade')
    st.markdown('## Anexar arquivo')
    file = st.file_uploader('Clique abaixo para importar seu arquivo', type='csv', )
    if file is not None:
        df = pd.read_csv(file, sep=';')
        st.markdown('## Linhas a serem visualizadas')
        slider = st.slider('Selecione o intervalo', 5, 100)
        st.dataframe(df.head(slider))
        st.markdown('## Coluna com os tempos a serem analisados')
        selected_time_column = st.selectbox('Coluna que contém os tempos dos códigos', df.columns)
        st.markdown('## Coluna com os códigos a serem analisados')
        selected_group_column = st.selectbox('Coluna que contém a informação dos códigos', df.columns)
        st.markdown('## Produto ou parada a ser analisada')
        option_cods = sorted(df[selected_group_column].unique())
        select = st.selectbox('Escolha o código a ser analisado:', option_cods)
        df_cod_filtered = df[df[selected_group_column] == select]
        st.table(df_cod_filtered.groupby(selected_group_column)[selected_time_column].describe())
        st.markdown('## Favor revisar os parâmetros abaixo, para uma análise mais assertiva dos dados:')
        df_min_column = int(df_cod_filtered[selected_time_column].min())
        df_max_column = int(df_cod_filtered[selected_time_column].max())
        df_min_value = st.number_input('Menor valor a ser considerado:', min_value=0, value=0)
        df_max_value = st.number_input('Maior valor a ser considerado:', min_value=df_min_column, value=df_max_column, max_value=df_max_column)
        st.markdown('### O step representa como os dados são agrupados, quanto menor o valor, mais colunas existirão:')
        df_step_value = st.number_input('Steps do histograma:', min_value=1, value=1)
        st.write(create_histogram(selected_time_column, df_cod_filtered, df_min_value, df_max_value, df_step_value))
        st.markdown('# Calculo de Eficiência')
        st.markdown('### Coluna que indica se a operação agrega ou não valor')
        selected_agregate_value_column = st.selectbox('Selecione a coluna na lista abaixo', df.columns)
        df_list_productive_time = df[df[selected_agregate_value_column] == 'S']
        df_list_unproductive_time = df[df[selected_agregate_value_column] == 'N']
        if not df_list_productive_time.empty:
            st.markdown('Apontamentos que agregam valor')
            df_sum_productive_time = df_list_productive_time.groupby(selected_agregate_value_column)[selected_time_column].sum()
            st.dataframe(df_sum_productive_time)
            st.markdown('Apontamentos que não agregam valor')
            st.dataframe(df_list_unproductive_time.groupby(selected_agregate_value_column)[selected_time_column].sum())
            st.markdown('### Tempo disponível para trabalho')
            work_days = st.number_input('Quantos dias de trabalho analisados?', min_value=0, value=0)
            work_min = st.number_input('Quantos minutos disponíveis de trabalho cada dia tem?', min_value=0, value=0)
            if work_min != 0 and work_days != 0:
                available_time_min = work_days * work_min
                st.markdown('## u1 = taxa de disponibilidade:')
                u1 = round(float((df_sum_productive_time / available_time_min) * 100), 2)
                st.write('##', u1, '%')
                st.markdown('### Coluna com os tempos de roteiro:')
                selected_script_time_column = st.selectbox('Selecione a coluna com os tempos de roteiro', df.columns)
                if df_list_productive_time[selected_script_time_column].dtypes == float or df_list_productive_time[selected_script_time_column].dtypes == int:
                    script_time = df_list_productive_time.groupby(selected_agregate_value_column)[selected_script_time_column].sum()
                    st.markdown('## u2 = taxa de performance:')
                    u2 = round(float((script_time / df_sum_productive_time) * 100), 2)
                    st.write('##', u2, '%')
                    st.markdown('### Coluna com a quantidade de peças não conformes:')
                    selected_ok_column = st.selectbox('Selecione a coluna com a quantidade de peças conforme', df.columns)
                    selected_nok_column = st.selectbox('Selecione a coluna com a quantidade de peças não conforme', df.columns)
                    selected_ok_column_is_number = df[selected_ok_column].dtypes == float or df[selected_ok_column].dtypes == int
                    selected_nok_column_is_number = df[selected_nok_column].dtypes == float or df[selected_nok_column].dtypes == int
                    if selected_ok_column_is_number and selected_nok_column_is_number:
                        df_list_ok_components = df[selected_ok_column].sum()
                        df_list_nok_components = df[selected_nok_column].sum()
                        if df_list_nok_components == 0:
                            df_list_nok_components = df_list_ok_components
                        st.markdown('## u3 = taxa de qualidade:')
                        u3 = round(100 - float((df_list_nok_components / df_list_ok_components) * 100), 2)
                        st.write('##', u3, '%')
                        st.markdown('# Eficiência Final (OEE)')
                        uf = round(((u1/100) * (u2/100) * (u3/100)) * 100, 2)
                        st.write('##', uf, '%')

if __name__ == '__main__':
    main()
