import { useState } from 'react'

const FilterSidebar = ({ filters, onFilterChange, onClearFilters }) => {
  const [isOpen, setIsOpen] = useState(false)

  const handleFilterChange = (key, value) => {
    onFilterChange({ ...filters, [key]: value })
  }

  const handleClearFilters = () => {
    onClearFilters()
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      {/* Mobile Toggle */}
      <div className="md:hidden mb-4">
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="w-full flex items-center justify-between p-3 bg-gray-50 rounded-lg"
        >
          <span className="font-medium">Filters</span>
          <svg
            className={`w-5 h-5 transition-transform ${isOpen ? 'rotate-180' : ''}`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </button>
      </div>

      {/* Filter Content */}
      <div className={`${isOpen ? 'block' : 'hidden'} md:block`}>
        {/* Size Filter */}
        <div className="mb-6">
          <h3 className="font-medium text-gray-900 mb-3">Size</h3>
          <div className="space-y-2">
            {['XS', 'S', 'M', 'L', 'XL', 'XXL'].map((size) => (
              <label key={size} className="flex items-center">
                <input
                  type="checkbox"
                  checked={filters.size === size}
                  onChange={() => handleFilterChange('size', filters.size === size ? '' : size)}
                  className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                />
                <span className="ml-2 text-sm text-gray-700">{size}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Color Filter */}
        <div className="mb-6">
          <h3 className="font-medium text-gray-900 mb-3">Color</h3>
          <div className="space-y-2">
            {[
              { name: 'Black', value: 'black' },
              { name: 'White', value: 'white' },
              { name: 'Red', value: 'red' },
              { name: 'Blue', value: 'blue' },
              { name: 'Green', value: 'green' },
              { name: 'Pink', value: 'pink' },
              { name: 'Purple', value: 'purple' },
              { name: 'Yellow', value: 'yellow' }
            ].map((color) => (
              <label key={color.value} className="flex items-center">
                <input
                  type="checkbox"
                  checked={filters.color === color.value}
                  onChange={() => handleFilterChange('color', filters.color === color.value ? '' : color.value)}
                  className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                />
                <span className="ml-2 text-sm text-gray-700">{color.name}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Price Range Filter */}
        <div className="mb-6">
          <h3 className="font-medium text-gray-900 mb-3">Price Range</h3>
          <div className="space-y-3">
            <div>
              <label className="block text-sm text-gray-700 mb-1">Min Price</label>
              <input
                type="number"
                placeholder="0"
                value={filters.price_min || ''}
                onChange={(e) => handleFilterChange('price_min', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-700 mb-1">Max Price</label>
              <input
                type="number"
                placeholder="1000"
                value={filters.price_max || ''}
                onChange={(e) => handleFilterChange('price_max', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
              />
            </div>
          </div>
        </div>

        {/* Material Filter */}
        <div className="mb-6">
          <h3 className="font-medium text-gray-900 mb-3">Material</h3>
          <div className="space-y-2">
            {[
              { name: 'Cotton', value: 'cotton' },
              { name: 'Polyester', value: 'polyester' },
              { name: 'Silk', value: 'silk' },
              { name: 'Wool', value: 'wool' },
              { name: 'Linen', value: 'linen' },
              { name: 'Denim', value: 'denim' }
            ].map((material) => (
              <label key={material.value} className="flex items-center">
                <input
                  type="checkbox"
                  checked={filters.material === material.value}
                  onChange={() => handleFilterChange('material', filters.material === material.value ? '' : material.value)}
                  className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                />
                <span className="ml-2 text-sm text-gray-700">{material.name}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Clear Filters Button */}
        <button
          onClick={handleClearFilters}
          className="w-full bg-gray-100 text-gray-700 hover:bg-gray-200 py-2 px-4 rounded-lg transition-colors duration-200"
        >
          Clear All Filters
        </button>
      </div>
    </div>
  )
}

export default FilterSidebar
