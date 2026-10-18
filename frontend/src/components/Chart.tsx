import Plotly from 'plotly.js/dist/plotly.min.js'
import createPlotlyComponent from 'react-plotly.js/factory'
import type { PlotlyFigure } from '../api/types'

const Plot = createPlotlyComponent(Plotly)

/**
 * House styling for the figures the API builds.
 *
 * Only presentation is touched: fonts, backgrounds, gridlines, hover and
 * margins. Traces, values and axis ranges come from the backend untouched, so
 * a chart always plots exactly what was calculated. `colorway` only applies to
 * traces that did not set their own colour.
 */
const HOUSE = {
  font: { family: "'IBM Plex Sans', ui-sans-serif, system-ui, sans-serif", size: 12, color: '#0f172a' },
  paper_bgcolor: 'rgba(0,0,0,0)',
  plot_bgcolor: 'rgba(0,0,0,0)',
  colorway: ['#1e40af', '#3b82f6', '#b45309', '#15803d', '#7c3aed', '#0e7490'],
  margin: { l: 56, r: 24, t: 48, b: 56 },
  hoverlabel: {
    bgcolor: '#0f172a',
    bordercolor: '#0f172a',
    font: { color: '#ffffff', family: "'IBM Plex Sans', sans-serif", size: 12 },
  },
  legend: { bgcolor: 'rgba(0,0,0,0)', borderwidth: 0 },
  xaxis: { gridcolor: '#e8eef7', zerolinecolor: '#c3cfe0', linecolor: '#dbe3ef', automargin: true },
  yaxis: { gridcolor: '#e8eef7', zerolinecolor: '#c3cfe0', linecolor: '#dbe3ef', automargin: true },
}

/** Renders Plotly figure JSON from the API (fig.to_json()). */
export default function Chart({ figure }: { figure: PlotlyFigure }) {
  const layout = {
    ...HOUSE,
    ...figure.layout,
    // Merge rather than replace, so the backend keeps its titles and ranges
    // while still picking up the gridline and margin styling.
    xaxis: { ...HOUSE.xaxis, ...(figure.layout.xaxis ?? {}) },
    yaxis: { ...HOUSE.yaxis, ...(figure.layout.yaxis ?? {}) },
    font: { ...HOUSE.font, ...(figure.layout.font ?? {}) },
    margin: { ...HOUSE.margin, ...(figure.layout.margin ?? {}) },
    autosize: true,
    width: undefined,
  }

  return (
    <Plot
      data={figure.data}
      layout={layout}
      useResizeHandler
      style={{ width: '100%' }}
      config={{ displaylogo: false, responsive: true, displayModeBar: 'hover' }}
    />
  )
}
