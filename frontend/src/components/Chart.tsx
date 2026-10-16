import Plotly from 'plotly.js/dist/plotly.min.js'
import createPlotlyComponent from 'react-plotly.js/factory'
import type { PlotlyFigure } from '../api/types'

const Plot = createPlotlyComponent(Plotly)

/** Renders Plotly figure JSON from the API (fig.to_json()). */
export default function Chart({ figure }: { figure: PlotlyFigure }) {
  return (
    <Plot
      data={figure.data}
      layout={{ ...figure.layout, autosize: true, width: undefined }}
      useResizeHandler
      style={{ width: '100%' }}
      config={{ displaylogo: false, responsive: true }}
    />
  )
}
