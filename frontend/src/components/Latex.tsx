import 'katex/dist/katex.min.css'
import { BlockMath, InlineMath } from 'react-katex'

/** Replaces st.latex. */
export default function Latex({ math, inline = false }: { math: string; inline?: boolean }) {
  return inline ? <InlineMath math={math} /> : <BlockMath math={math} />
}
