import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import { Package } from 'lucide-react'
import KpiCard from '../KpiCard'

describe('KpiCard', () => {
  it('renders the title and value', () => {
    render(
      <KpiCard
        title="Total Products"
        value="42"
        icon={Package}
        color="border-blue-500"
      />,
    )
    expect(screen.getByText('Total Products')).toBeInTheDocument()
    expect(screen.getByText('42')).toBeInTheDocument()
  })

  it('applies the color class to the card border', () => {
    const { container } = render(
      <KpiCard
        title="Low Stock"
        value="3"
        icon={Package}
        color="border-red-500"
      />,
    )
    expect(container.firstChild).toHaveClass('border-red-500')
  })

  it('renders the supplied lucide icon as an svg', () => {
    const { container } = render(
      <KpiCard
        title="Stock Value"
        value="€12,345"
        icon={Package}
        color="border-green-500"
      />,
    )
    expect(container.querySelector('svg')).toBeInTheDocument()
  })
})
