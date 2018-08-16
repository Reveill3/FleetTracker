const webpack = require('webpack');
const path = require('path');
const CleanWebpackPlugin = require('clean-webpack-plugin');


module.exports = {
  entry: {
    main: './ui/index.js',
    vendor: [
      'react', 'react-dom'
    ]
  },
  output: {
    path: path.resolve(__dirname, 'static/build'),
    filename: "[name].[chunkhash].js"
  },
  module: {
    rules: [
      {
        test: /\.jsx?$/,
        exclude: /node_modules/,
        use: [
          {
            loader: 'babel-loader',
            options: {
            presets: ['env', 'react', 'stage-0']
            }
          }
        ],
      }
    ]
  },
  plugins: [
    new CleanWebpackPlugin(['static/build']),
    new webpack.optimize.SplitChunksPlugin({
      name: 'vendor'
    }),
    new webpack.optimize.SplitChunksPlugin({
      name: 'runtime'
    }),
  ]
}