%%
% Function returning random integer in the specified range
% @param min_value: minimum value in the range
% @param max_value: maximum value in the range
% @return: integer in range from Min to Max (inclusive)
function y = MyRnd (min_value, max_value)
    y = min_value + floor(rand*(max_value-min_value+1));
endfunction